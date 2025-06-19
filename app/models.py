from datetime import datetime
from sqlalchemy import Boolean, Column, DateTime, String

from database import Base


class AccessGrant(Base):
    __tablename__ = "access_grants"
    uuid = Column(String, primary_key=True, index=True)
    granted = Column(Boolean, default=True)


class SuccessfulSpellIP(Base):
    __tablename__ = "successful_spell_ips"
    ip = Column(String, primary_key=True, index=True)
    user_uuid = Column(String)
    cast_time = Column(DateTime, default=datetime.utcnow)
