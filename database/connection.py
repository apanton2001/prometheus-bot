import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables
load_dotenv()

# Get database URL from environment or use default SQLite database
def get_database_url():
    """Get database URL from environment variables or use default SQLite database"""
    db_user = os.getenv("DB_USER", "")
    db_pass = os.getenv("DB_PASS", "")
    db_host = os.getenv("DB_HOST", "")
    db_port = os.getenv("DB_PORT", "")
    db_name = os.getenv("DB_NAME", "")
    
    # If PostgreSQL configuration is available, use it
    if db_user and db_pass and db_host and db_port and db_name:
        return f"postgresql://{db_user}:{db_pass}@{db_host}:{db_port}/{db_name}"
    
    # Otherwise use SQLite
    base_dir = Path(__file__).resolve().parent.parent
    return f"sqlite:///{base_dir}/prometheus.db"

# Create engine and session factory
engine = create_engine(get_database_url())
session_factory = sessionmaker(bind=engine)
Session = scoped_session(session_factory)

def get_db_session():
    """Get a new database session"""
    return Session()

def close_db_session(session):
    """Close a database session"""
    session.close()

def init_db():
    """Initialize the database"""
    from .schema import Base
    Base.metadata.create_all(engine)

if __name__ == "__main__":
    # Initialize the database if this file is run directly
    from .schema import init_db
    init_db(engine)
    print("Database initialized successfully") 