# likemodas/db/session.py
from contextlib import contextmanager
from sqlmodel import create_engine, Session
import os

DATABASE_URL = os.getenv("DB_URL")
if not DATABASE_URL:
    raise ValueError("DB_URL environment variable not set.")
    
engine = create_engine(DATABASE_URL)

@contextmanager
def get_db_session():
    session = Session(engine)
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()