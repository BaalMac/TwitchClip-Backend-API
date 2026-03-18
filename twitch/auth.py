import requests
from datetime import datetime, timedelta, timezone
from config import Config
from logger import logger
from twitch.tokenCrypt import encrypt_token, decrypt_token
from database.connection import Session
from database.models import TwitchToken
from sqlalchemy import select

def get_twitch_token():
    session = Session()
    try:

        token_row = session.execute(select(TwitchToken)).scalars().first()

        if token_row and token_row.expires_at > datetime.utcnow():
            logger.debug   ('Reusing stored token from database')
            return token_row.access_token            

        logger.info('Fetching new Twitch Oauth Token')
        r = requests.post('https://id.twitch.tv/oauth2/token', params={
            'client_id': Config.TWITCH_CLIENT_ID,
            'client_secret': Config.TWITCH_CLIENT_SECRET,
            'grant_type': 'client_credentials'
        })

        data = r.json()
        encrypted = encrypt_token(data['access_token'])
        expires_at = datetime.utcnow() + timedelta(seconds=data['expires_in'])

        if token_row:
            token_row.access_token = encrypted
            token_row.expires_at = expires_at
        else:
            token_row = TwitchToken(
                access_token = encrypted,
                expires_at = expires_at
            )
            session.add(token_row)
        
        session.commit()
        logger.info(f'New token stored, expires at {expires_at}')
        return encrypted
    
    finally:
        session.close()