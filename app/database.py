import os
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

Base = declarative_base()
_engine = None
_SessionLocal = None


def init_engine() -> None:
    """Create engine and sessionmaker if they don't exist."""
    global _engine, _SessionLocal
    db_url = os.getenv("DATABASE_URL", "sqlite:///./app.db")
    if _engine is None or str(_engine.url) != db_url:
        connect_args = {"check_same_thread": False} if db_url.startswith("sqlite") else {}
        _engine = create_engine(db_url, connect_args=connect_args)
        _SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=_engine)
        Base.metadata.create_all(_engine)


def get_sessionmaker():
    init_engine()
    return _SessionLocal


def get_session():
    Session = get_sessionmaker()
    db = Session()
    try:
        yield db
    finally:
        db.close()
