from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database import Base
from app.state_persistence import AccessStateDB, SuccessfulSpellIPsDB


class TestAccessStateDB:
    def test_round_trip(self, tmp_path):
        db_url = f"sqlite:///{tmp_path}/test.db"
        engine = create_engine(db_url, connect_args={"check_same_thread": False})
        Session = sessionmaker(bind=engine)
        Base.metadata.create_all(engine)

        session = Session()
        state = AccessStateDB(session)
        state["abc"] = True
        assert state.get("abc") is True
        session.close()

        session2 = Session()
        state2 = AccessStateDB(session2)
        assert state2.get("abc") is True
        session2.close()


class TestSuccessfulSpellIPsDB:
    def test_membership_persistence(self, tmp_path):
        db_url = f"sqlite:///{tmp_path}/ip.db"
        engine = create_engine(db_url, connect_args={"check_same_thread": False})
        Session = sessionmaker(bind=engine)
        Base.metadata.create_all(engine)

        session = Session()
        ips = SuccessfulSpellIPsDB(session)
        ip = "127.0.0.1"
        ips[ip] = {"user_uuid": "u1", "cast_time": datetime.utcnow()}
        assert ip in ips
        session.close()

        session2 = Session()
        ips2 = SuccessfulSpellIPsDB(session2)
        assert ip in ips2
        session2.close()
