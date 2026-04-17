from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os
from pathlib import Path

# Load .env
load_dotenv()

# Read full URL from env, fallback to local SQLite so auth/progress always works.
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL")
if not SQLALCHEMY_DATABASE_URL:
    db_path = Path(__file__).resolve().parent / "formfix.db"
    SQLALCHEMY_DATABASE_URL = f"sqlite:///{db_path}"

# Engine
connect_args = {}
if SQLALCHEMY_DATABASE_URL and SQLALCHEMY_DATABASE_URL.startswith("mysql"):
    connect_args = {"connect_timeout": 2}
if SQLALCHEMY_DATABASE_URL and SQLALCHEMY_DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

try:
    engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args=connect_args)
    with engine.connect():
        pass
except Exception:
    # If the configured DB is unreachable, fallback to local SQL DB.
    db_path = Path(__file__).resolve().parent / "formfix.db"
    SQLALCHEMY_DATABASE_URL = f"sqlite:///{db_path}"
    engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})

# Session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class
Base = declarative_base()

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
