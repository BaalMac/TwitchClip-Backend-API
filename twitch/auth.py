import requests
from config import Config

def get_twitch_token():
    r = requests.post('https://id.twitch.tv/oauth2/token', params={
        'client_id': Config.TWITCH_CLIENT_ID,
        'client_secret': Config.TWITCH_CLIENT_SECRET,
        'grant_type': 'client_credentials'
    })
    return r.json()
    # instead of returning to JSON it should update the database but the token should be encrypted
