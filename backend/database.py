from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import sys
from pathlib import Path

# Add root directory to sys.path to allow config import
sys.path.append(str(Path(__file__).resolve().parent.parent))
import config

engine = create_engine(
    config.DATABASE_URL,
    connect_args={"check_same_thread": False} if config.DATABASE_URL.startswith("sqlite") else {}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
