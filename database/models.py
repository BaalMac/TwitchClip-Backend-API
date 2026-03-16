from sqlalchemy import Column, String, Text, DateTime, Integer
from database.connection import Base
from datetime import datetime, timezone

class Clip(Base):
    __tablename__ = 'clips'

    id = Column(String(255), primary_key=True)
    url = Column(Text, nullable=False)
    embed_url = Column(Text, nullable=False)
    created_at = Column(DateTime, nullable=False)
    fetched_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    vod_id = Column(String(255), nullable=True)
    vod_offset = Column(Integer, nullable=True)

class TwitchToken(Base):
    __tablename__ = 'twitch_token'

    id = Column(Integer, primary_key=True, autoincrement=True)
    access_token = Column(Text, nullable=False)
    expires_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))