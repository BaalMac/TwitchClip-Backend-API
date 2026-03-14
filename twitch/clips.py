import requests
from config import Config
from logger import logger
from twitch.mockup import requestURL_MOCK

Authentication = {
    'Authorization': f'Bearer {Config.TWITCH_TOKEN}', 
    'Client-Id': Config.TWITCH_CLIENT_ID
}

def requestURL(link):

    clipID=  link.split('/')[-1]
    r = requests.get(f'https://api.twitch.tv/helix/clips?id={clipID}', headers=Authentication)

    remaining = int(r.headers.get('Ratelimit-Remaining', 100))
    reset = r.headers.get('Ratelimit-Reset')
    status = r.status_code
    logger.info(f'[{status}] Clip: {clipID} | Remaining: {remaining} | Reset: {reset}')

    if status == 200:
        if remaining < 100:
            logger.warning(f"[{status}] Approaching rate limit - only {remaining} requests left")
        return r.json

    elif status == 401:
        logger.error(f"[{status}] Token is expired, renewing...")
        # [FUTURE IMPLIMENTATION]
        # calls Auth.py for to reauthenticate and update database tables
        # loops back to RequestURL

    elif status == 404:
        logger.error(f'[{status}] Clip not found')

    elif status == 429:
        wait = int(reset) - int(time.time())
        logger.error(f"[{status}] Rate limited - Waiting {wait}s before retry")
        time.sleep(wait)
        return requestURL(link)
    
    else:
        logger.error(f"[{status}] Unexpected status code {status} for the Clip")
        return None
 
def GrabInfo(link):
    #data = requestURL(link)
    data = requestURL_MOCK(1)
    if 'error' in data:
        return "Something went wrong with the TwitchAPI! Check Logs"
    else:
        user = data['data'][0]
        return {
            'id': user['id'],
            'url': user['url'],
            'embed_url': user['embed_url'],
            'broadcaster_id': user['broadcaster_id'],
            "Streamer": user['broadcaster_name'],
            'VOD_ID': user['video_id'],
            'clip_created': user['created_at']
        }