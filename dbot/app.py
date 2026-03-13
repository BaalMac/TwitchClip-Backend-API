'''
Before separating the individual define function
Start creating the Entire code here

Plans:
- Communicate with Discord bot
- Setup Twitch API to call the Twitch Clip.
- Communicate with Main Python Flask
- Twitch Clip Validation and information Grabing

ONCE THE MAIN FUNCTION IS COMPLETE - ENGAGE ZERO TRUST INPUT - CLEAN/VALIDATE ALL INPUTS 
'''
import requests
from config import Config

def example():
    return Config.TWITCH_CLIENT_ID