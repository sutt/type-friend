import os
import logging
from datetime import datetime
from sqlalchemy import create_engine, Column, String, Boolean, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker


Base = declarative_base()
_engine = None
_SessionLocal = None

logger = logging.getLogger(__name__)


def reset_engine():
    global _engine, _SessionLocal
    if _engine is not None:
        _engine.dispose()
    _engine = None
    _SessionLocal = None


def _build_database_url():
    """Build database URL from individual DB_ environment variables or fallback to DATABASE_URL."""
    db_host = os.getenv("DB_HOST")
    db_port = os.getenv("DB_PORT")
    db_name = os.getenv("DB_NAME")
    db_user = os.getenv("DB_USER")
    db_password = os.getenv("DB_PASSWORD")
    db_url = os.getenv("DATABASE_URL")
    
    if db_url is not None:
        return db_url
    elif all([db_host, db_name, db_user]):
        port_part = f":{db_port}" if db_port else ""
        password_part = f":{db_password}" if db_password else ""
        user_part = f"{db_user}{password_part}"
        return f"postgresql+psycopg2://{user_part}@{db_host}{port_part}/{db_name}"
    else:
        logger.warning(
            "DB_URL or DB_HOST/DB_NAME/DB_USER not set; "
            "defaulting to sqlite db: app.db"
        )
        return "sqlite:///./app.db"


def get_engine():
    global _engine, _SessionLocal
    if _engine is None:
        db_url = _build_database_url()
        connect_args = {}
        if db_url.startswith("sqlite"):
            connect_args["check_same_thread"] = False
        _engine = create_engine(db_url, connect_args=connect_args)
        _SessionLocal = sessionmaker(bind=_engine)
    return _engine


def get_session():
    if _SessionLocal is None:
        get_engine()
    return _SessionLocal()


def init_db():
    engine = get_engine()
    Base.metadata.create_all(bind=engine)


class UserAccess(Base):
    __tablename__ = "user_access"

    uuid = Column(String, primary_key=True)
    granted = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class SuccessfulSpellIP(Base):
    __tablename__ = "successful_spell_ips"

    ip = Column(String, primary_key=True)
    user_uuid = Column(String)
    cast_time = Column(DateTime, default=datetime.utcnow)


class AccessStore:
    def __init__(self, session):
        self.session = session

    def __contains__(self, key: str) -> bool:
        return self.session.query(UserAccess).filter_by(uuid=key).first() is not None

    def __setitem__(self, key: str, value: bool) -> None:
        obj = self.session.query(UserAccess).filter_by(uuid=key).first()
        if obj is None:
            obj = UserAccess(uuid=key, granted=value)
            self.session.add(obj)
        else:
            obj.granted = value
        self.session.commit()

    def get(self, key: str, default=None):
        obj = self.session.query(UserAccess).filter_by(uuid=key).first()
        return obj.granted if obj else default


class SpellIPStore:
    def __init__(self, session):
        self.session = session

    def __contains__(self, key: str) -> bool:
        return self.session.query(SuccessfulSpellIP).filter_by(ip=key).first() is not None

    def __setitem__(self, key: str, value: dict) -> None:
        obj = self.session.query(SuccessfulSpellIP).filter_by(ip=key).first()
        if obj is None:
            obj = SuccessfulSpellIP(ip=key, user_uuid=value.get("user_uuid"), cast_time=value.get("cast_time"))
            self.session.add(obj)
        else:
            obj.user_uuid = value.get("user_uuid")
            obj.cast_time = value.get("cast_time")
        self.session.commit()

    def get(self, key: str, default=None):
        obj = self.session.query(SuccessfulSpellIP).filter_by(ip=key).first()
        if obj is None:
            return default
        return {"user_uuid": obj.user_uuid, "cast_time": obj.cast_time}
