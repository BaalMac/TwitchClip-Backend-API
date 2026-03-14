import requests
from config import Config

Authentication = {
    'Authorization': f'Bearer {Config.TWITCH_TOKEN}', 
    'Client-Id': Config.TWITCH_CLIENT_ID
}

def requestURL(link):
    '''
    [WORKS] Python Sucessfully Calling TwitchAPI

    clipID=  link.split('/')[-1]
    r = requests.get(f'https://api.twitch.tv/helix/clips?id={clipID}', headers=Authentication)
    return r.json()
    '''

    # For now since i dont want to call the API everytime i want to experiment with my code. I return what a return should look like
    return {
        'data': [
            {
                'id': 'BigAgitatedRadishRickroll-ZGx1a1Y5-oXkypwj', 
                'url': 'https://www.twitch.tv/lucypyre/clip/BigAgitatedRadishRickroll-ZGx1a1Y5-oXkypwj', 
                'embed_url': 'https://clips.twitch.tv/embed?clip=BigAgitatedRadishRickroll-ZGx1a1Y5-oXkypwj', 
                'broadcaster_id': '696039109', 
                'broadcaster_name': 'LucyPyre', 
                'creator_id': '472183', 
                'creator_name': 'Omnislasher', 
                'video_id': '2721318188', 
                'game_id': '509658', 
                'language': 'en', 
                'title': 'Skinny maxxing Numi', 
                'view_count': 75, 
                'created_at': '2026-03-13T17:08:46Z', 
                'thumbnail_url': 'https://static-cdn.jtvnw.net/twitch-video-assets/twitch-vap-video-assets-prod-us-west-2/30e70847-e827-443d-a7ca-94ae181104bc/landscape/thumb/thumb-0000000000-480x272.jpg', 
                'duration': 41.3, 
                'vod_offset': 2204, 
                'is_featured': False
            }], 'pagination': {}
            }
    #This should return in the event that the PythonAPI DOES interact with TwitchAPI but throws an error
    #return {'error': 'Unauthorized', 'status': 401, 'message': 'OAuth token is missing'}

def GrabInfo(link):
    data = requestURL(link)
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
'''
Notes
    Mari Mari Clip ID"  FragileBlitheSeahorsePermaSmug-8KGBa6SdLZyfuGmg
    Lucy Pyre Clip Link: https://www.twitch.tv/lucypyre/clip/BigAgitatedRadishRickroll-ZGx1a1Y5-oXkypwj

Before separating the individual define function
Start creating the Entire code here

Plans: 
- Setup Database structure
- Call Database events such as [Event_History] and [Event_Time]
and return them as a JSON format
- Communicate to Discord bot

ONCE THE MAIN FUNCTION IS COMPLETE - ENGAGE ZERO TRUST INPUT - CLEAN/VALIDATE ALL INPUTS
Note to self: 
> Impliment rate limiting in API
'''