import os
from datetime import datetime
from sqlalchemy import create_engine, Column, String, Boolean, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker


Base = declarative_base()
_engine = None
_SessionLocal = None


def reset_engine():
    global _engine, _SessionLocal
    if _engine is not None:
        _engine.dispose()
    _engine = None
    _SessionLocal = None


def get_engine():
    global _engine, _SessionLocal
    if _engine is None:
        db_url = os.getenv("DATABASE_URL", "sqlite:///./app.db")
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
