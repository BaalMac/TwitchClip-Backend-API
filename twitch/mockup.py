from logger import logger
def requestURL_MOCK(link):
    if link == 0:
        logger.info('[200] Clip: BigAgitatedRadishRickroll-ZGx1a1Y5-oXkypwj | Remaining: 6969 | Reset: idk')
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
                    'vod_offset': 2204, # offset in seconds
                    'is_featured': False
                }], 'pagination': {}
                }
    else:
        #This should return in the event that the PythonAPI DOES interact with TwitchAPI but throws an error
        logger.warning("[401] Token is expired, renewing...")
        return {'error': 'Unauthorized', 'status': 401, 'message': 'OAuth token is missing'}