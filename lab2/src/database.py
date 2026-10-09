import os
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# Configurable database URL: prefers PostgreSQL, falls back gracefully for standalone testing
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///lab2_hr.db")

# SQLite needs check_same_thread=False for multithreading
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(DATABASE_URL, echo=False, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    """Dependency / context helper for database sessions."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
