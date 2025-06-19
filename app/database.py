import os
from datetime import datetime

from sqlalchemy import (
    create_engine,
    MetaData,
    Table,
    Column,
    String,
    Boolean,
    DateTime,
    insert,
    select,
    update,
)
from sqlalchemy.orm import sessionmaker

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./app.db")

connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
engine = create_engine(DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(bind=engine)

metadata = MetaData()

user_access_table = Table(
    "user_access",
    metadata,
    Column("uuid", String, primary_key=True),
    Column("granted", Boolean, nullable=False, default=False),
)

successful_spell_ips_table = Table(
    "successful_spell_ips",
    metadata,
    Column("ip", String, primary_key=True),
    Column("user_uuid", String, nullable=False),
    Column("cast_time", DateTime, nullable=False),
)


def init_db(engine_override=None):
    """Create database tables."""
    metadata.create_all(engine_override or engine)


class UserAccessState:
    """Dictionary-like access state persisted in the database."""

    def __init__(self, engine=engine):
        self.engine = engine
        self.Session = sessionmaker(bind=engine)

    def __setitem__(self, uuid: str, granted: bool):
        with self.Session() as session:
            exists = session.execute(
                select(user_access_table.c.uuid).where(user_access_table.c.uuid == uuid)
            ).scalar()
            if exists is not None:
                session.execute(
                    update(user_access_table)
                    .where(user_access_table.c.uuid == uuid)
                    .values(granted=granted)
                )
            else:
                session.execute(
                    insert(user_access_table).values(uuid=uuid, granted=granted)
                )
            session.commit()

    def get(self, uuid: str, default=None):
        with self.Session() as session:
            result = session.execute(
                select(user_access_table.c.granted).where(
                    user_access_table.c.uuid == uuid
                )
            ).scalar()
            return default if result is None else result


class SuccessfulSpellIPsState:
    """Dictionary-like IP tracking persisted in the database."""

    def __init__(self, engine=engine):
        self.engine = engine
        self.Session = sessionmaker(bind=engine)

    def __contains__(self, ip: str) -> bool:
        with self.Session() as session:
            return (
                session.execute(
                    select(successful_spell_ips_table.c.ip).where(
                        successful_spell_ips_table.c.ip == ip
                    )
                ).scalar()
                is not None
            )

    def __setitem__(self, ip: str, value: dict):
        with self.Session() as session:
            exists = session.execute(
                select(successful_spell_ips_table.c.ip).where(
                    successful_spell_ips_table.c.ip == ip
                )
            ).scalar()
            if exists is not None:
                session.execute(
                    update(successful_spell_ips_table)
                    .where(successful_spell_ips_table.c.ip == ip)
                    .values(user_uuid=value["user_uuid"], cast_time=value["cast_time"])
                )
            else:
                session.execute(
                    insert(successful_spell_ips_table).values(
                        ip=ip, user_uuid=value["user_uuid"], cast_time=value["cast_time"]
                    )
                )
            session.commit()

    def get(self, ip: str, default=None):
        with self.Session() as session:
            row = session.execute(
                select(
                    successful_spell_ips_table.c.user_uuid,
                    successful_spell_ips_table.c.cast_time,
                ).where(successful_spell_ips_table.c.ip == ip)
            ).first()
            if row:
                return {"user_uuid": row.user_uuid, "cast_time": row.cast_time}
            return default

