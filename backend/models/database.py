import os
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.pool import StaticPool

Base = declarative_base()


def get_database_url():
    """Get database URL from environment or use default SQLite."""
    database_url = os.environ.get('DATABASE_URL')
    
    if database_url:
        return database_url
    
    # Default to SQLite in /data directory
    data_dir = os.environ.get('DATA_DIR', '/data')
    os.makedirs(data_dir, exist_ok=True)
    return f'sqlite:///{data_dir}/secrets.db'


def init_db():
    """Initialize database and create all tables."""
    database_url = get_database_url()
    
    if 'sqlite' in database_url:
        engine = create_engine(
            database_url,
            connect_args={'check_same_thread': False},
            poolclass=StaticPool
        )
    else:
        engine = create_engine(database_url)
    
    Base.metadata.create_all(engine)
    return engine


def get_session_factory(engine):
    """Get SQLAlchemy session factory."""
    return sessionmaker(autocommit=False, autoflush=False, bind=engine)
