from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from config import Config

# The engine is your actual connection to the database.
# Think of it like opening a phone line to PostgreSQL.
engine = create_engine(Config.DATABASE_URL)

# A session is how you send instructions down that phone line.
# Every time you want to read or write data, you open a session.
Session = sessionmaker(bind=engine)

# Base is the parent class all your models will inherit from.
# It's how SQLAlchemy knows which Python classes map to which DB tables.
Base = declarative_base()

def init_db():
    from database.models import Clip, TwitchToken
    Base.metadata.create_all(engine)