# starts the program

from dbot.app import example
from twitch import clips, auth, tokenCrypt
from config import Config
from logger import logger
from database.connection import init_db
from twitch.mockup import requestURL_MOCK
from twitch.auth import get_twitch_token
from twitch.tokenCrypt import encrypt_token, decrypt_token
from datetime import datetime, timezone, timedelta

#print(example())
#link is a twitch Clip as a placeholder for now
link = 'https://www.twitch.tv/lucypyre/clip/BigAgitatedRadishRickroll-ZGx1a1Y5-oXkypwj'
if __name__ == '__main__':
    logger.info('Starting up...')
    init_db()
    logger.info('Database initialized successfully')



