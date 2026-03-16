'''
Config.py holding data for .env so that the rest of the API can grab the vital information
For now since this is still in development. the Config.py will be holding all the information
Once During Production, Separate the data to where the machines with the Application, only has
its necessary credentials to function. (dont forget to recreate .env once in production)
'''
import os
from dotenv import load_dotenv

load_dotenv()
class Config:
    API_PORT     = os.getenv('API_PORT', 5000)  # ← 5000 is the default port for Flask
    SECRET_KEY   = os.getenv('SECRET_KEY')
    DATABASE_URL = os.getenv('DATABASE_URL')

    DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')

    TWITCH_CLIENT_ID = os.getenv('TWITCH_CLIENT_ID')
    TWITCH_CLIENT_SECRET = os.getenv('TWITCH_CLIENT_SECRET')
    TWITCH_TOKEN = os.getenv('TWITCH_TOKEN')
    TWITCH_TOKEN_TYPE = os.getenv('TWITCH_TOKEN_TYPE')

    ENCRYPTION_KEY = os.getenv('ENCRYPTION_KEY')