from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool
from app.database import metadata, UserAccessState, SuccessfulSpellIPsState


def test_user_access_persists():
    engine = create_engine(
        "sqlite:///:memory:", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    metadata.create_all(engine)
    access = UserAccessState(engine)
    access["u1"] = True
    assert access.get("u1") is True


def test_successful_spell_ip_persists():
    engine = create_engine(
        "sqlite:///:memory:", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    metadata.create_all(engine)
    ips = SuccessfulSpellIPsState(engine)
    now = datetime.utcnow()
    ips["1.2.3.4"] = {"user_uuid": "u1", "cast_time": now}
    assert "1.2.3.4" in ips
    data = ips.get("1.2.3.4")
    assert data["user_uuid"] == "u1"

from fastapi.testclient import TestClient
from app.key_buffer_manager import KeyBufferManager
from main import (
    app,
    get_key_buffer_manager,
    get_user_access_state,
    get_successful_spell_ips_state,
)


def test_state_updated_after_spell(simple_spell):
    engine = create_engine(
        "sqlite:///:memory:", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    metadata.create_all(engine)
    manager = KeyBufferManager(parsed_secret_spell=simple_spell)
    access_state = UserAccessState(engine)
    ips_state = SuccessfulSpellIPsState(engine)
    app.dependency_overrides[get_key_buffer_manager] = lambda: manager
    app.dependency_overrides[get_user_access_state] = lambda: access_state
    app.dependency_overrides[get_successful_spell_ips_state] = lambda: ips_state
    client = TestClient(app)
    uuid = "db-spell"
    for key in simple_spell:
        client.post("/keypress", json={"key": key, "uuid": uuid})

    assert access_state.get(uuid) is True
    app.dependency_overrides.clear()
