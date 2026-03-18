import requests
from config import Config
from logger import logger
from twitch import auth, tokenCrypt
from database.connection import Session
from database.models import TwitchToken, Clip
from sqlalchemy import select, func
from datetime import datetime, timezone

#TESTSITE
from twitch.mockup import requestURL_MOCK

def requestURL(link: str):
    session = Session()
    try: 
        tToken = tokenCrypt.decrypt_token(auth.get_twitch_token())

        Authentication = {
        'Authorization': f'Bearer {tToken}', 
        'Client-Id': Config.TWITCH_CLIENT_ID
        }

        clipID=  link.split('/')[-1]

        r = requests.get(f'https://api.twitch.tv/helix/clips?id={clipID}', headers=Authentication)

        remaining = int(r.headers.get('Ratelimit-Remaining', 100))
        reset = r.headers.get('Ratelimit-Reset')
        status = r.status_code
        logger.info(f'[{status}] Clip: {clipID} | Remaining: {remaining} | Reset: {reset}')

        if status == 200:
            if remaining < 100:
                logger.warning(f"[{status}] Approaching rate limit - only {remaining} requests left")
            return r.json()

        elif status == 404:
            logger.error(f'[{status}] Clip not found')
            return {"Error": status}

        elif status == 429:
            wait = 90 # Hard codes wait for 90 seconds and will try again
            logger.warning(f"[{status}] Rate limited - Waiting {wait}s before retry")
            time.sleep(wait)
            return requestURL(link)
        
        else:
            logger.error(f"[{status}] Unexpected status code {status} for the Clip")
            return {"Error": status}

    except Exception as e:
        logger.error(f'The API shit the bed (Specifically at requestURL function): {link}: {e}')
        return {'success': False, 'Error': str(e)}
 
    finally:
        session.close()

def SaveClip(link: str):
    session = Session()
    try:
        data = requestURL(link)

        if data.get("Error") is not None:
            return {'Success': False, 'error': f"Error Code: {data["Error"]} Check Logs"}
        
        clip_data = data['data'][0]
        existing = session.execute(select(Clip).where(Clip.id == clip_data['id'])).scalars().first()

        if existing:
            logger.info(f"Clip ID: {clip_data["id"]} already exists in the Database - Skipping")
            return {'Success': False, 'error': "Clip already Exists"}

        clip = Clip(
            id = clip_data["id"],
            url = clip_data["url"],
            embed_url = clip_data["embed_url"],
            created_at = clip_data["created_at"],
            vod_id = clip_data.get("vod_id"),
            vod_offset = clip_data.get("vod_offset")
        )
        
        session.add(clip)
        session.commit()
        logger.info(f"Clip {clip_data["id"]} saved successfully!")

        if clip_data.get('vod_id') is None or clip_data.get('vod_offset') is None:
            logger.warning(f'Clip {clip_data["id"]} saved but vod data is null — PythonAPI will retry later')
            return {'success': True, 'vod_pending': True, 'clip_id': clip_data['id']}

        return {'success': True, 'vod_pending': False, 'clip_id': clip_data['id']}

    except Exception as e:
        session.rollback()
        logger.error(f'The API shit the Bed (Specifically at SaveClip Function): {link}: {e}')
        return {'success': False, 'error': str(e)}

    finally:
        session.close()
 

def UpdateVodData():
    session = Session()
    try:
        pending_clips = session.execute(select(Clip).where(Clip.vod_id == None)).scalars().all()
        
        if not pending_clips:
            logger.info('No pending clips found')
            return
        
        logger.info(f"Found {len(pending_clips)} clips with missing vod data")

        for clip in pending_clips:
            data = requestURL(clip.id)

            if data is None:
                logger.warning(f'Could not fetch clip ID {clip.id}, skipping')
                continue
            
            clip_data = data["data"][0]

            if clip_data.get("vod_id") is None or clip_data.get("vod_offset") is None:
                logger.info(f"VOD data still null for {clip.id}, will try later")
                continue
            
            clip.vod_id = clip_data["vod_id"]
            clip.vod_offset = clip_data['vod_offset']
            session.commit()
            logger.info(f"Updated VOD data for clip {clip.id}")
    
    except Exception as e:
        session.rollback()
        logger.error(f"The API shit the Bed (Specifically at UpdateVodData Function): {e}")
    
    finally:
        session.close()

def UpdateClip(clip_link: str, new_link: str):
    session = Session()
    try:
        clip_id = clip_link.split('/')[-1]

        existing = session.execute(select(Clip).where(Clip.id == clip_id)).scalars().first()

        if existing is None:
            logger.error(f"Clip {clip_id} not found in database")
            return {'success': False, "error": f"Clip ID: {clip_id} not found in database"}
        
        data = requestURL(new_link)

        if data.get("Error") is not None:
            logger.error(f"Requested Clip Returned Error. Check Logs")
            return {'Success': False, 'error': f"Could not fetch clip data {new_link}. Check Logs"}
        
        clip_data = data["data"][0]

        existing.id = clip_data['id']
        existing.url = clip_data['url']
        existing.embed_url = clip_data['embed_url']
        existing.created_at = clip_data['created_at']
        existing.vod_id = clip_data.get('vod_id')
        existing.vod_offset = clip_data.get('vod_offset')
        existing.fetched_at = datetime.now(timezone.utc)

        session.commit()
        logger.info(f"Clip {clip_id} has been sucessfully replaced with {clip_data['id']}")

        if clip_data.get('vod_id') is None or clip_data.get('vod_offset') is None:
            logger.warning(f'Updated clip {clip_data["id"]} has NULL VOD Data, will try later')
            return {'success': True, 'vod_pending': True, 'clip_id': clip_data['id']}

        return {'success': True, 'vod_pending': False, 'clip_id': clip_data['id']}
 
    except Exception as e:
        session.rollback()
        logger.error(f"The API shit the Bed (Specifically at UpdateClip Function): {e}")
        return {'success': False, 'error': str(e)}
    
    finally:
        session.close()


def RemoveClip(clip_link: str):
    session = Session()
    try:
        clip_id =  clip_link.split('/')[-1]

        existing = session.execute(select(Clip).where(Clip.id == clip_id)).scalars().first()

        if existing is None:
            logger.error(f"RemoveClip failed - clip {clip_id} not found in database")
            return {'error': f"Clip {clip_id} does not exist in the database"}
        
        session.delete(existing)
        session.commit()
        logger.info(f'Clip {clip_id} removed successfully')
        return {'success': True, 'message': f'Clip {clip_id} removed successfully'}
    
    except Exception as e:
        session.rollback()
        logger.error(f'The API shit the Bed (Specifically at RemoveClip Function): {e}')
        return {'success': False, 'error': str(e)}

    finally:
        session.close()

def GetClips(limit: int = 10, offset: int = 0):
    session = Session()
    try:
        total_count = session.execute(select(func.count()).select_from(Clip)).scalar()

        clips = session.execute(
            select(Clip)
            .order_by(Clip.created_at.desc())
            .limit(limit)
            .offset(offset)
        ).scalars().all()

        if not clips:
            logger.info(f'No Clips found at offset {offset}')
            return {
                'success': True,
                'clips': [],
                'total': total_count,
                'limit': limit,
                'offset': offset,
                'has_more': False
            }
        parsed_clips = []
        for clip in clips:
            parsed_clips.append({
                'id': clip.id,
                'url': clip.url,
                'embed_url': clip.embed_url,
                'created_at': clip.created_at.isoformat(),
                'fetched_at': clip.fetched_at.isoformat() if clip.fetched_at else None,
                'vod_id': clip.vod_id,
                'vod_offset': clip.vod_offset
            })
        has_more = (offset + limit) < total_count
        logger.info(f'Returned {len(parsed_clips)} clips | offset: {offset} | total: {total_count}')
        return {
            'success': True,
            'clips': parsed_clips,
            'total': total_count,
            'limit': limit,
            'offset': offset,
            'has_more': has_more
        }

    except Exception as e:
        logger.error(f"The API shit the Bed (Specifically at GetClips Function): {e}")
        return {'success': False, 'error': str(e)}
    
    finally:
        session.close()