import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Update with your actual PostgreSQL connection string (see Option 1 or Option 2 in earlier instructions)
DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://postgres:mypassword@localhost/game_db')

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()