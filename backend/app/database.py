import os
from sqlalchemy import create_engine, text  # Added 'text' here
from sqlalchemy.orm import sessionmaker, declarative_base
from .models import Base # Ensure this import is here

SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    with engine.connect() as connection:
        # Enable the vector extension first!
        connection.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
        connection.commit()
    # Create the tables second!
    Base.metadata.create_all(bind=engine)