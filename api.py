from flask import Flask, jsonify, request
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from twitch.clips import GetClips
from config import Config
from logger import logger

app = Flask(__name__)

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

if __name__ == '__main__':
    logger.info(f"Starting Flask on 0.0.0.0:{Config.API_PORT}")
    app.run(host='0.0.0.0', port=Config.API_PORT, debug=False)