import os
import logging
from datetime import datetime

def setup_logger():
    os.makedirs('logs', exist_ok=True)
    logger = logging.getLogger('twitch_bot')
    logger.setLevel(logging.DEBUG)

    # Format for each log line
    formatter = logging.Formatter(
        '[%(asctime)s] [%(levelname)s] %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # Log to file
    file_handler = logging.FileHandler(f'logs/PythonAPI.log')
    file_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    return logger

logger = setup_logger()