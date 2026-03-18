# Twitch Clip Backend API

A Python backend for fetching, storing, and managing Twitch clip metadata via the Twitch Helix API. Built with Flask, SQLAlchemy, and PostgreSQL.

> 🤖 **Implementing Discord bot to talk to the API soon**

---

## Table of Contents

- [Stack](#stack)
- [Project Structure](#project-structure)
- [Setup](#setup)
- [Environment Variables](#environment-variables)
- [Database](#database)
- [Running the App](#running-the-app)
- [API Endpoints](#api-endpoints)
- [clips.py Function Reference](#clipspy-function-reference)
- [Security](#security)
- [Notes](#notes)

---

## Stack

| Layer | Technology |
|---|---|
| Language | Python 3.11+ |
| API Framework | Flask |
| ORM | SQLAlchemy |
| Database | PostgreSQL |
| Rate Limiting | Flask-Limiter |
| Encryption | cryptography (Fernet) |
| Proxy | Nginx |
| DNS / DDoS | Cloudflare |

---

## Project Structure

```
project/
├── bot/
│   ├── __init__.py
│   └── discord_bot.py          # Discord bot (coming soon)
│
├── twitch/
│   ├── __init__.py
│   ├── auth.py                 # OAuth token fetch, cache, and DB storage
│   ├── clips.py                # Core clip logic — save, update, remove, fetch
│   └── tokenCrypt.py           # Fernet encrypt/decrypt for token storage
│
├── database/
│   ├── __init__.py
│   ├── connection.py           # SQLAlchemy engine, session, Base
│   └── models.py               # Clip and TwitchToken table models
│
├── logs/
│   └── twitch_bot.log          # Auto-generated at runtime
│
├── api.py                      # Flask API — public and protected endpoints
├── config.py                   # Config class reading from .env
├── logger.py                   # Logging setup — file + console output
├── run.py                      # Entry point — initializes DB and starts Flask
├── nginx.conf                  # Nginx reverse proxy and Slow Loris config
├── .env                        # Secret — never commit this
├── .env.example                # Safe template for teammates
├── .gitignore
└── requirements.txt
```

---

## Setup

**1. Clone the repo and install dependencies:**
```bash
git clone https://github.com/yourname/yourrepo.git
cd yourrepo
pip install -r requirements.txt
```

**2. Copy the environment template and fill in your values:**
```bash
cp .env.example .env
```

**3. Set up PostgreSQL:**
```bash
sudo -u postgres psql
```
```sql
CREATE DATABASE twitchbot;
CREATE USER twitchuser WITH PASSWORD 'yourpassword';
GRANT ALL PRIVILEGES ON DATABASE twitchbot TO twitchuser;
\c twitchbot
GRANT ALL ON SCHEMA public TO twitchuser;
GRANT USAGE ON SCHEMA public TO twitchuser;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO twitchuser;
\q
```

**4. Generate an encryption key for token storage:**
```bash
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```
Paste the output into your `.env` as `ENCRYPTION_KEY`.

---

## Environment Variables

```env
API_PORT=5000
API_HOST=0.0.0.0
SECRET_KEY=

DATABASE_URL=postgresql://twitchuser:yourpassword@localhost/twitchbot

TWITCH_CLIENT_ID=
TWITCH_CLIENT_SECRET=

ENCRYPTION_KEY=
DISCORD_API_KEY=
```

---

## Database

Tables are created automatically on first run via SQLAlchemy. No manual SQL needed after the initial PostgreSQL setup.

**`clips` table:**

| Column | Type | Description |
|---|---|---|
| `id` | VARCHAR(255) PK | Twitch clip ID |
| `url` | TEXT | Direct clip URL |
| `embed_url` | TEXT | Embeddable iframe URL |
| `created_at` | TIMESTAMP WITH TZ | When Twitch created the clip |
| `fetched_at` | TIMESTAMP WITH TZ | When the record was stored |
| `vod_id` | VARCHAR(255) nullable | Source VOD ID — may be null on new clips |
| `vod_offset` | INTEGER nullable | Timestamp in source VOD — may be null on new clips |

**`twitch_tokens` table:**

| Column | Type | Description |
|---|---|---|
| `id` | INTEGER PK | Always 1 — single row |
| `access_token` | TEXT | Encrypted Fernet token |
| `expires_at` | TIMESTAMP WITH TZ | Token expiry (~64 days from issue) |
| `created_at` | TIMESTAMP WITH TZ | When the token was stored |

---

## Running the App

**Development:**
```bash
python run.py
```

> 🐳 **Docker support coming soon**

---

## API Endpoints

Base URL: `http://localhost:5000`

### Available

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/clips` | Fetch paginated clips |

**Query parameters for `GET /clips`:**

| Parameter | Default | Description |
|---|---|---|
| `limit` | `10` | Number of clips to return |
| `offset` | `0` | Number of clips to skip |

**Example request:**
```bash
curl http://localhost:5000/clips?limit=10&offset=0
```

**Example response:**
```json
{
    "success": true,
    "clips": [
        {
            "id": "FragileBlitheSeahorse",
            "url": "https://clips.twitch.tv/FragileBlitheSeahorse",
            "embed_url": "https://clips.twitch.tv/embed?clip=FragileBlitheSeahorse",
            "created_at": "2026-03-14T12:00:00+00:00",
            "fetched_at": "2026-03-14T12:05:00+00:00",
            "vod_id": "123456789",
            "vod_offset": 360
        }
    ],
    "total": 42,
    "limit": 10,
    "offset": 0,
    "has_more": true
}
```

---

### Coming Soon

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/clips` | Save a new clip |
| `PUT` | `/clips/<clip_id>` | Replace an existing clip |
| `DELETE` | `/clips/<clip_id>` | Remove a clip |
| `POST` | `/clips/vod/update` | Trigger VOD data update for pending clips |

---

## clips.py Function Reference

All core clip logic lives in `twitch/clips.py`.

---

### `requestURL(link: str) -> dict | None`

Calls the Twitch Helix API for a clip by ID. Handles all status codes, rate limiting, and logging.

```python
from twitch.clips import requestURL

data = requestURL('FragileBlitheSeahorse')
```

| Status | Behaviour |
|---|---|
| `200` | Returns JSON response dict |
| `401` | Logs error, returns `None` |
| `404` | Logs error, returns `None` |
| `429` | Waits 90 seconds, retries once |
| Other | Logs error, returns `None` |

---

### `SaveClip(link: str) -> dict`

Fetches clip data from Twitch and saves it to the database. Skips duplicates. Saves immediately even if `vod_id` and `vod_offset` are null — `UpdateVodData()` fills those in later.

```python
from twitch.clips import SaveClip

result = SaveClip('https://twitch.tv/clip/FragileBlitheSeahorse')
print(result)
# {'success': True, 'vod_pending': False, 'clip_id': 'FragileBlitheSeahorse'}
```

**Returns:**
```json
{ "success": true,  "vod_pending": false, "clip_id": "FragileBlitheSeahorse" }
{ "success": true,  "vod_pending": true,  "clip_id": "FragileBlitheSeahorse" }
{ "success": false, "error": "Clip already exists" }
{ "success": false, "error": "Could not fetch clip data" }
```

---

### `UpdateClip(clip_id: str, new_link: str) -> dict`

Finds an existing clip by ID and replaces all its data with the new clip fetched from Twitch.

```python
from twitch.clips import UpdateClip

result = UpdateClip('FragileBlitheSeahorse', 'https://twitch.tv/clip/NewClipID')
print(result)
# {'success': True, 'vod_pending': False, 'clip_id': 'NewClipID'}
```

**Returns:**
```json
{ "success": true,  "clip_id": "NewClipID" }
{ "success": false, "error": "Clip FragileBlitheSeahorse not found in database" }
{ "success": false, "error": "Could not fetch clip data for new link" }
```

---

### `RemoveClip(clip_id: str) -> dict`

Deletes a clip from the database by ID. Returns both an error log and a clean message if the clip does not exist.

```python
from twitch.clips import RemoveClip

result = RemoveClip('FragileBlitheSeahorse')
print(result)
# {'success': True, 'message': 'Clip FragileBlitheSeahorse removed successfully'}
```

**Returns:**
```json
{ "success": true,  "message": "Clip FragileBlitheSeahorse removed successfully" }
{ "success": false, "error": "Clip FragileBlitheSeahorse does not exist in the database" }
```

---

### `GetClips(limit: int = 10, offset: int = 0) -> dict`

Returns a paginated list of clips from the database ordered by `created_at` descending (newest first). Used by the frontend for infinite scrolling.

```python
from twitch.clips import GetClips

result = GetClips(limit=10, offset=0)
print(result['has_more'])   # True — more clips available
print(result['total'])      # Total clips in DB
```

**Returns:**
```json
{
    "success": true,
    "clips": [...],
    "total": 42,
    "limit": 10,
    "offset": 0,
    "has_more": true
}
```

The `has_more` field tells the frontend when to stop triggering infinite scroll loads.

---

### `UpdateVodData() -> None`

Queries the database for all clips where `vod_id` is `NULL`, re-fetches each one from Twitch, and updates the row if the VOD data has populated. Leaves clips untouched if VOD data is still null — safe to call repeatedly.

```python
from twitch.clips import UpdateVodData

UpdateVodData()
# Logs: UpdateVodData — found 3 clips with missing vod data
# Logs: UpdateVodData — updated vod data for clip FragileBlitheSeahorse
# Logs: UpdateVodData — vod data still null for OtherClip, will retry later
```

VOD data on recently created Twitch clips can take several minutes to populate. This function is designed to be called on a timer to keep retrying until all pending clips are resolved.

---

## Security

| Layer | Technology | Protects against |
|---|---|---|
| DNS / CDN | Cloudflare | DDoS, bot traffic, WAF |
| Firewall | UFW | Direct server access bypassing Cloudflare |
| Reverse proxy | Nginx | Slow Loris, connection floods, path scanners |
| Rate limiting | Flask-Limiter | Endpoint abuse per IP |
| Token encryption | Fernet (cryptography) | DB breach exposing live tokens |
| ORM | SQLAlchemy | SQL injection via parameterized queries |
| Proxy headers | ProxyFix + CloudflareProxyFix | IP spoofing via forged headers |

---

## Notes

- `vod_id` and `vod_offset` are nullable — Twitch does not populate these immediately on clip creation. `UpdateVodData()` handles backfilling them.
- The Twitch OAuth token is encrypted with Fernet before being stored in the database. It is only decrypted in memory at request time.
- Twitch rate limit is 100 requests per minute on the clips endpoint. The `requestURL()` function handles 429 responses automatically with a 90 second wait and one retry.