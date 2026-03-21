# starts the program
import threading
import subprocess
from config import Config
from logger import logger
from database.connection import init_db
import api

def start_api():
    from api import app
    logger.info(f"Starting Flask on 0.0.0.0:{Config.API_PORT}")
    app.run(host='0.0.0.0', port=Config.API_PORT, debug=False)

if __name__ == '__main__':
    logger.info('Starting up Database...')
    init_db()
    logger.info('Database initialized successfully')
    logger.info('Starting Gunicorn...')
    try:
        subprocess.run([
            'gunicorn',
            '--workers',    '4',          # 4 worker processes
            '--bind',       '0.0.0.0:5000',
            '--timeout',    '30',         # Kill workers that take longer than 30s
            '--access-logfile', 'logs/gunicorn_access.log',
            '--error-logfile',  'logs/gunicorn_error.log',
            '--log-level',  'debug',
            'api:app'                     # module:flask_app_variable
        ])
    except KeyboardInterrupt:
        logger.info('Shutting down — goodbye')