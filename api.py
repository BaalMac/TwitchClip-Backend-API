from flask import Flask, jsonify, request
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from twitch.clips import GetClips
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

@app.route('/clips', methods=['GET'])
@limiter.limit('30 per minute')
def get_clips():
    limit = request.args.get('limit', 10, type = int)
    offset = request.args.get('offset', 0, type = int)
    result = GetClips(limit, offset)
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

