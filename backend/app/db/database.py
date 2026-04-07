from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .models import Base
import os

# Defaults to local SQLite for easy development. 
# In production/Docker, we will pass a PostgreSQL URL via .env
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./undersec.db")

connect_args = {"check_same_thread": False} if "sqlite" in DATABASE_URL else {}
engine = create_engine(DATABASE_URL, connect_args=connect_args)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    """Creates all tables if they don't exist."""
    Base.metadata.create_all(bind=engine)

def get_db():
    """Dependency to get the database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()