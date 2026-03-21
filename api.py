from flask import Flask, jsonify, request
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from twitch.clips import GetClips, SaveClip, UpdateClip, RemoveClip, UpdateVodData
from functools import wraps
from config import Config
from logger import logger
import logging

app = Flask(__name__)

# Trust Cloudflare's forwarded IP header
from wsgi_cloudflare_proxy_fix import CloudflareProxyFix
from werkzeug.middleware.proxy_fix import ProxyFix
app.wsgi_app = CloudflareProxyFix(app.wsgi_app, log_level=logging.INFO)
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1)

# Request size limit For future implimentation when adding a POST command
app.config['MAX_CONTENT_LENGTH'] = 1 * 1024 * 1024

limiter = Limiter(
    get_remote_address,
    app = app,
    default_limits = ["100 per minute", "800 per day"],
    storage_uri='memory://'
)

def require_api_key(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        key = request.headers.get('X-API-Key')

        if not key:
            logger.warning(f'Rejected request to {request.path} — no API key provided')
            return jsonify({'success': False, 'error': 'API key required'}), 401

        if key != Config.DISCORD_API_KEY:
            logger.warning(f'Rejected request to {request.path} — invalid API key')
            return jsonify({'success': False, 'error': 'Invalid API key'}), 403

        return f(*args, **kwargs)
    return decorated

# -------------------------------------------------------
# PUBLIC — no API key needed
# Website calls this for infinite scrolling
# -------------------------------------------------------

@app.route('/clips', methods=['GET'])
@limiter.limit('30 per minute')
def get_clips():
    limit = request.args.get('limit', 6, type = int)
    offset = request.args.get('offset', 0, type = int)
    result = GetClips(limit, offset)
    return jsonify(result)

# -------------------------------------------------------
# PRIVATE — API key required
# Only your Discord bot can call these
# -------------------------------------------------------
@app.route('/clips', methods=['POST'])
@limiter.limit('20 per minute')
@require_api_key
def save_clip():
    data   = request.get_json()
    link   = data.get('link')
    result = SaveClip(link)
    return jsonify(result)

@app.route('/clips/vod/update', methods=['POST'])
@require_api_key
def update_vod_data():
    UpdateVodData()
    return jsonify({'success': True, 'message': 'Vod data update triggered'})

@app.route('/clips/<clip_id>', methods=['PUT'])
@require_api_key
def update_clip(clip_id):
    data     = request.get_json()
    new_link = data.get('link')
    result   = UpdateClip(clip_id, new_link)
    return jsonify(result)

@app.route('/clips/<clip_id>', methods=['DELETE'])
@require_api_key
def remove_clip(clip_id):
    result = RemoveClip(clip_id)
    return jsonify(result)

@app.errorhandler(429)
def rate_limit_exceeded(e):
    logger.warning(f'Rate limit exceeded from IP: {get_remote_address()}')
    return jsonify({
        'success': False,
        'error': 'Too many request - CHILL THE FUCK OUT BRO',
        'retry_after': e.description
    }), 429

@app.errorhandler(413)
def request_too_large(e):
    return jsonify({'success': False, 'error': 'Request too large'}), 413

# removes Flask Default server header
@app.after_request
def remove_server_header(response):
    response.headers.pop('Server', None)
    response.headers.pop('X-Powered-By', None)
    return response

