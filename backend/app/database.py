import os
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:YOUR_PASSWORD@localhost:5432/agroflow"
)


def create_db_engine(url: str):
    # Fallback list for PostgreSQL drivers (supports psycopg2, pure-python pg8000)
    drivers = []
    if url.startswith("postgresql://"):
        drivers = [
            url.replace("postgresql://", "postgresql+pg8000://", 1),
            url.replace("postgresql://", "postgresql+psycopg2://", 1),
            url,
        ]
    elif "postgresql+psycopg2://" in url:
        drivers = [
            url,
            url.replace("postgresql+psycopg2://", "postgresql+pg8000://", 1)
        ]
    else:
        drivers = [url]

    for driver_url in drivers:
        try:
            eng = create_engine(driver_url, pool_pre_ping=True)
            return eng
        except Exception:
            continue

    return create_engine(url, pool_pre_ping=True)


engine = create_db_engine(DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
