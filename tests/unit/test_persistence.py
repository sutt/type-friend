import os
from datetime import datetime
from app import database


def test_access_store_persistence(tmp_path):
    db_url = f"sqlite:///{tmp_path}/db.sqlite"
    os.environ["DATABASE_URL"] = db_url
    database.reset_engine()
    database.init_db()

    session1 = database.get_session()
    store1 = database.AccessStore(session1)
    store1["test-uuid"] = True
    session1.close()

    session2 = database.get_session()
    store2 = database.AccessStore(session2)
    assert store2.get("test-uuid") is True
    session2.close()


def test_spell_ip_store_persistence(tmp_path):
    db_url = f"sqlite:///{tmp_path}/db.sqlite"
    os.environ["DATABASE_URL"] = db_url
    database.reset_engine()
    database.init_db()

    session1 = database.get_session()
    store1 = database.SpellIPStore(session1)
    store1["127.0.0.1"] = {"user_uuid": "u1", "cast_time": datetime.utcnow()}
    session1.close()

    session2 = database.get_session()
    store2 = database.SpellIPStore(session2)
    assert "127.0.0.1" in store2
    assert store2.get("127.0.0.1")["user_uuid"] == "u1"
    session2.close()
