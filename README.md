# TwitchClip Backend API

A production-ready Python REST API for fetching, storing, and managing Twitch clip metadata via the Twitch Helix API. Built with Flask, SQLAlchemy, and PostgreSQL — deployable via Docker containers and designed to work behind Cloudflare for DDoS protection and CDN delivery.

The API exposes a public `GET /clips` endpoint consumable by any frontend (including Cloudflare Pages sites), while all write operations are protected and accessible through authenticated clients such as a Discord bot.

> 🤖 **A [Discord bot](https://github.com/BaalMac/DiscordBot-Call-API) is currently being used to save, update, and remove clips directly from a Discord server.**

---

## Table of Contents

- [Stack](#stack)
- [Project Structure](#project-structure)
- [How It Works](#how-it-works)
- [Setup](#setup)
- [Environment Variables](#environment-variables)
- [Database](#database)
- [Running the App](#running-the-app)
- [Deployment](#deployment)
- [API Endpoints](#api-endpoints)
- [clips.py Function Reference](#clipspy-function-reference)
- [Security](#security)
- [Notes](#notes)

---

## Stack

| Layer | Technology |
|---|---|
| Language | Python 3.11+ |
| API Framework | Flask + Gunicorn |
| ORM | SQLAlchemy |
| Database | PostgreSQL |
| Rate Limiting | Flask-Limiter |
| Encryption | cryptography (Fernet) |
| Reverse Proxy | Nginx |
| DNS / DDoS / CDN | Cloudflare |
| Containerization | Docker + Docker Compose |
| Hosting | Railway (API + DB) |

---

## Project Structure

```
TwitchClip-Backend-API/
│
├── twitch/
│   ├── __init__.py
│   ├── auth.py                 # OAuth2 token fetch, encryption, DB storage
│   ├── clips.py                # Core clip logic — save, update, remove, fetch
│   └── tokenCrypt.py           # Fernet encrypt/decrypt for token at rest
│
├── database/
│   ├── __init__.py
│   ├── connection.py           # SQLAlchemy engine, session, Base
│   └── models.py               # Clip and TwitchToken table models
│
├── logs/
│   └── app.log                 # Auto-generated at runtime
│
├── api.py                      # Flask API — routes, CORS, rate limiting
├── config.py                   # Config class reading from .env
├── logger.py                   # Logging setup — file + console output
├── run.py                      # Entry point — init DB and start Gunicorn
├── nginx.conf                  # Nginx reverse proxy and Slow Loris config
├── Dockerfile                  # Docker container definition
├── .env                        # Secret — never commit this
├── .env.example                # Safe template for teammates
├── .gitignore
└── requirements.txt
```

---

## How It Works

The API has two tiers of access designed to support any kind of client:

```
Cloudflare Pages / Any Browser
    → GET /clips (public)
        → Returns paginated clip metadata for infinite scroll

Discord Bot / Authenticated Client
    → POST, PUT, DELETE /clips (protected via X-API-Key)
        → Full clip management — save, update, remove, trigger VOD backfill
```

The `GET /clips` endpoint is intentionally public so any frontend — including static sites hosted on **Cloudflare Pages** — can fetch and display clips without authentication. All write operations require an `X-API-Key` header, making them accessible only to trusted clients like a Discord bot, a management dashboard, or any other authenticated service you build on top of the API.

**Traffic routing in production:**

```
Internet
    → Cloudflare (DDoS, WAF, CDN)
        → Nginx (Slow Loris, connection limits) — port 80
            → Gunicorn (WSGI) — port 5000
                → Flask → clips.py → PostgreSQL
```

---

## Setup

**1. Clone the repo:**
```bash
git clone https://github.com/BaalMac/TwitchClip-Backend-API.git
cd TwitchClip-Backend-API
git checkout security
```

**2. Install dependencies:**
```bash
pip install -r requirements.txt
```

**3. Copy the environment template:**
```bash
cp .env.example .env
```

**4. Set up PostgreSQL:**
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

**5. Generate an encryption key for Twitch token storage:**
```bash
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```
Paste the output into your `.env` as `ENCRYPTION_KEY`.

**6. Generate an API key for protected routes:**
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```
Paste the output into your `.env` as `DISCORD_API_KEY`.

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

CUSTOM_DOMAIN=https://yourdomain.com
CLOUDFLARE_PAGES_URL=https://yoursite.pages.dev
```

---

## Database

Tables are created automatically on first run via SQLAlchemy. No manual SQL needed beyond the initial PostgreSQL user and database setup.

**`clips` table:**

| Column | Type | Description |
|---|---|---|
| `id` | VARCHAR(255) PK | Twitch clip ID — used as primary key directly |
| `url` | TEXT | Direct clip URL |
| `embed_url` | TEXT | Embeddable iframe URL |
| `title` | TEXT nullable | Clip title from Twitch API |
| `created_at` | TIMESTAMP WITH TZ | When Twitch created the clip |
| `fetched_at` | TIMESTAMP WITH TZ | When the record was stored locally |
| `vod_id` | VARCHAR(255) nullable | Source VOD ID — may be null on new clips |
| `vod_offset` | INTEGER nullable | Timestamp offset in source VOD — may be null on new clips |

**`twitch_tokens` table:**

| Column | Type | Description |
|---|---|---|
| `id` | INTEGER PK | Always 1 — single row |
| `access_token` | TEXT | Fernet-encrypted OAuth2 token |
| `expires_at` | TIMESTAMP WITH TZ | Token expiry (~64 days from issue) |
| `created_at` | TIMESTAMP WITH TZ | When the token was stored |

---

## Running the App

**Development:**
```bash
python run.py
```

**Kill any existing process on port 5000 if needed:**
```bash
sudo pkill gunicorn
```

---

## Deployment

### Docker

The project is fully containerized and deployable with Docker Compose. Each service runs in its own isolated container:

```bash
# Build and start all services
docker compose up --build

# Stop all services
docker compose down
```

Services defined in `docker-compose.yml`:

| Service | Description |
|---|---|
| `db` | PostgreSQL database with persistent volume |
| `api` | Flask + Gunicorn application server |
| `nginx` | Reverse proxy — handles public traffic routing |

> 🐳 **When running with Docker, update `DATABASE_URL` in your `.env` to use the service name instead of localhost:**
> ```
> DATABASE_URL=postgresql://twitchuser:yourpassword@db/twitchbot
> ```

---

### Railway

The API is deployable directly to Railway. Connect your GitHub repository to a Railway project and set all environment variables in the Railway dashboard. Railway handles the container orchestration and provides a public URL automatically.

Internal service communication on Railway uses the service name as the hostname (e.g. `http://twitchbot-api:5000`) — this allows a Discord bot deployed as a separate Railway service to communicate with the API over Railway's private network without exposing port 5000 publicly.

---

### Cloudflare Pages (Frontend)

For frontends hosted on Cloudflare Pages, the public `GET /clips` endpoint is CORS-enabled. Set `CLOUDFLARE_PAGES_URL` in your `.env` to your Pages deployment URL to allow cross-origin requests from your frontend.

Your frontend only needs two lines to connect:

```javascript
const API_URL  = 'https://your-api-domain.com';
const response = await fetch(`${API_URL}/clips?limit=6&offset=0`);
const data     = await response.json();
```

---

## API Endpoints

Base URL: `https://your-api-domain.com`

### Public

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/clips` | Fetch paginated clips ordered by newest first |

**Query parameters:**

| Parameter | Default | Description |
|---|---|---|
| `limit` | `6` | Number of clips per page |
| `offset` | `0` | Number of clips to skip |

**Example:**
```bash
curl "https://your-api-domain.com/clips?limit=6&offset=0" | python3 -m json.tool
```

**Response:**
```json
{
    "success": true,
    "clips": [
        {
            "id": "LuckyPopularCroissantBudStar-BwIz3r_Pu2YhF0rw",
            "url": "https://www.twitch.tv/henyathegenius/clip/LuckyPopularCroissantBudStar-BwIz3r_Pu2YhF0rw",
            "embed_url": "https://clips.twitch.tv/embed?clip=LuckyPopularCroissantBudStar-BwIz3r_Pu2YhF0rw",
            "title": "DAYO 😭😭😭😭😭",
            "created_at": "2026-03-14T12:00:00+00:00",
            "fetched_at": "2026-03-14T12:05:00+00:00",
            "vod_id": "123456789",
            "vod_offset": 360
        }
    ],
    "total": 42,
    "limit": 6,
    "offset": 0,
    "has_more": true
}
```

The `has_more` field signals whether more clips exist — use it to drive infinite scrolling on your frontend.

---

### Protected

All protected routes require the `X-API-Key` header. These are intended for authenticated clients — the Discord bot is the primary example, but any service with the key can call them.

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/clips` | Save a new clip by Twitch URL |
| `PUT` | `/clips/<clip_id>` | Replace an existing clip with a new one |
| `DELETE` | `/clips/<clip_id>` | Remove a clip by ID |
| `POST` | `/clips/vod/update` | Trigger VOD data backfill for pending clips |

**Save a clip:**
```bash
curl -X POST https://your-api-domain.com/clips \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your_api_key_here" \
  -d '{"link": "https://www.twitch.tv/channel/clip/ClipID"}' \
  | python3 -m json.tool
```

**Replace a clip:**
```bash
curl -X PUT https://your-api-domain.com/clips/OldClipID \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your_api_key_here" \
  -d '{"link": "https://www.twitch.tv/channel/clip/NewClipID"}' \
  | python3 -m json.tool
```

**Remove a clip:**
```bash
curl -X DELETE https://your-api-domain.com/clips/ClipID \
  -H "X-API-Key: your_api_key_here" \
  | python3 -m json.tool
```

**Trigger VOD backfill:**
```bash
curl -X POST https://your-api-domain.com/clips/vod/update \
  -H "X-API-Key: your_api_key_here" \
  | python3 -m json.tool
```

---

## clips.py Function Reference

All core clip logic lives in `twitch/clips.py`.

---

### `requestURL(link: str) -> dict`

Calls the Twitch Helix API for a clip. Handles all status codes, rate limiting, and logging internally.

| Status | Behaviour |
|---|---|
| `200` | Returns full JSON response |
| `401` | Logs error, returns `{'Error': 401}` |
| `404` | Logs error, returns `{'Error': 404}` |
| `429` | Waits 90 seconds, retries automatically |
| Other | Logs error, returns `{'Error': status}` |

---

### `SaveClip(link: str) -> dict`

Fetches clip metadata from Twitch and saves it to the database. Skips duplicates. Saves immediately even if `vod_id` and `vod_offset` are null — `UpdateVodData()` backfills those later.

```json
{ "success": true,  "vod_pending": false, "clip_id": "ClipID" }
{ "success": true,  "vod_pending": true,  "clip_id": "ClipID" }
{ "success": false, "error": "Clip already Exists" }
```

---

### `UpdateClip(clip_id: str, new_link: str) -> dict`

Finds an existing clip by ID and replaces all its data with fresh metadata fetched from the new Twitch URL.

```json
{ "success": true,  "vod_pending": false, "clip_id": "NewClipID" }
{ "success": false, "error": "Clip ID: OldClipID not found in database" }
```

---

### `RemoveClip(clip_id: str) -> dict`

Deletes a clip by ID. Returns a clean message if the clip does not exist rather than crashing.

```json
{ "success": true,  "message": "Clip ClipID removed successfully" }
{ "success": false, "error": "Clip ClipID does not exist in the database" }
```

---

### `GetClips(limit: int = 6, offset: int = 0) -> dict`

Returns a paginated list of clips ordered by `created_at` descending — newest clips first. The `has_more` field tells the frontend when to stop infinite scrolling.

```json
{
    "success": true,
    "clips": [...],
    "total": 42,
    "limit": 6,
    "offset": 0,
    "has_more": true
}
```

---

### `UpdateVodData() -> None`

Queries the database for all clips where `vod_id` is `NULL`, re-fetches each one from Twitch, and updates the row when VOD data has populated. Safe to call repeatedly — clips with still-null VOD data are left untouched and retried on the next call.

Twitch does not populate `vod_id` and `vod_offset` immediately on clip creation. This function handles the eventual consistency by backfilling when the data becomes available.

---

## Security

| Layer | Technology | Protects against |
|---|---|---|
| DNS / CDN | Cloudflare | DDoS, bot traffic, WAF rules |
| Firewall | UFW | Direct server access bypassing Cloudflare |
| Reverse proxy | Nginx | Slow Loris, connection floods, scanner paths |
| Rate limiting | Flask-Limiter | Per-IP endpoint abuse |
| API key | `X-API-Key` header | Unauthorized write access |
| Token encryption | Fernet (cryptography) | DB breach exposing live OAuth tokens |
| ORM | SQLAlchemy | SQL injection via parameterized queries |
| Proxy headers | ProxyFix + CloudflareProxyFix | IP spoofing via forged forwarded headers |
| Request limits | Flask + Nginx | Oversized payload attacks |

---

## Notes

- Twitch clip IDs are used directly as the database primary key — no auto-generated IDs needed since Twitch guarantees uniqueness.
- The Twitch OAuth2 token is encrypted with Fernet before being written to the database. It is decrypted in memory only at request time and never logged or returned in any API response.
- `vod_id` and `vod_offset` are nullable — Twitch does not populate these immediately on clip creation. `UpdateVodData()` handles backfilling them once Twitch makes the data available.
- Twitch's rate limit on the clips endpoint is 100 requests per minute. The `requestURL()` function handles `429` responses automatically with a hardcoded 90 second wait before retrying.
- The `GET /clips` endpoint is public and CORS-enabled for browser-based frontends including Cloudflare Pages. All other endpoints require the `X-API-Key` header and are intended for server-to-server communication only.