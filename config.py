import os
from dotenv import load_dotenv

load_dotenv()
class Config:
    API_PORT     = os.getenv('API_PORT', 5000)  # ← 5000 is the default port for Flask

    DATABASE_URL = os.getenv('DATABASE_URL')

    DISCORD_API_KEY = os.getenv('DISCORD_API_KEY')

    TWITCH_CLIENT_ID = os.getenv('TWITCH_CLIENT_ID')
    TWITCH_CLIENT_SECRET = os.getenv('TWITCH_CLIENT_SECRET')

    ENCRYPTION_KEY = os.getenv('ENCRYPTION_KEY')

    CLOUDFLARE_PAGES_URL = os.getenv("CLOUDFLARE_PAGES_URL")
    CUSTOM_DOMAIN = os.getenv("CUSTOM_DOMAIN")