"""Postgres Database Configuration Module"""

import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import ProgrammingError

load_dotenv(dotenv_path="app/.env")

# Load environment variables
POSTGRES_URL = os.getenv('POSTGRES_URL',"sqlite:///./test.db")
DB_NAME = os.getenv('POSTGRES_DB')

# Create engine without specifying the database name (for creating the database if not exists)
engine_without_db = create_engine(POSTGRES_URL.rsplit('/', 1)[0])
engine = create_engine(POSTGRES_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def create_database_if_not_exists():
    "Function to create the database if it does not exist"
    try:
        with engine_without_db.connect() as conn:
            conn.execute(text("COMMIT"))
            result = conn.execute(
                text(f"SELECT 1 FROM pg_database WHERE datname = '{DB_NAME}'")
            ).fetchone()
            if not result:
                conn.execute(text(f"CREATE DATABASE {DB_NAME}"))
                conn.execute(text("COMMIT"))  # Commit the database creation
                print(f"Database '{DB_NAME}' created successfully.")
            else:
                print(f"Database '{DB_NAME}' already exists.")
    except ProgrammingError as e:
        print(f"Failed to check or create the database: {e}")


def get_postgres_db():
    "Function to create a session for the database"
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()