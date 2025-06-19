import os
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch
from uvicorn.middleware.proxy_headers import ProxyHeadersMiddleware
from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool

from app.database import (
    metadata,
    UserAccessState,
    SuccessfulSpellIPsState,
)

# Import your app components
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "app"))

from main import (
    app,
    get_key_buffer_manager,
    get_user_access_state,
    get_successful_spell_ips_state,
)
from key_buffer_manager import KeyBufferManager


@pytest.fixture
def sqlite_engine():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    metadata.create_all(engine)
    yield engine
    engine.dispose()


@pytest.fixture
def test_client(sqlite_engine):
    """Create a test client for FastAPI app using SQLite."""
    app.dependency_overrides[get_user_access_state] = lambda: UserAccessState(sqlite_engine)
    app.dependency_overrides[get_successful_spell_ips_state] = lambda: SuccessfulSpellIPsState(sqlite_engine)
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


@pytest.fixture
def simple_spell():
    """Simple spell sequence for testing."""
    return ["a", "b", "Enter"]


@pytest.fixture
def konami_code_spell():
    """The actual Konami code from .env.example."""
    return [
        "ArrowUp",
        "ArrowUp",
        "ArrowDown",
        "ArrowDown",
        "ArrowLeft",
        "ArrowRight",
        "ArrowLeft",
        "ArrowRight",
        "b",
        "a",
        "Enter",
    ]


@pytest.fixture
def clean_key_buffer_manager(simple_spell):
    """Create a fresh KeyBufferManager instance for each test."""
    return KeyBufferManager(parsed_secret_spell=simple_spell)


@pytest.fixture
def test_uuid():
    """Consistent UUID for testing."""
    return "test-uuid-12345"




@pytest.fixture
def test_client_with_custom_spell(sqlite_engine):
    """Create a test client with custom spell configuration."""
    # Create singleton instance for this test
    test_manager_instance = None
    test_access_state_instance = UserAccessState(sqlite_engine)
    test_successful_spell_ips_instance = SuccessfulSpellIPsState(sqlite_engine)

    def create_custom_key_buffer_manager(spell_sequence=None):
        nonlocal test_manager_instance
        if test_manager_instance is None:
            if spell_sequence is None:
                spell_sequence = ["x", "y", "z"]
            test_manager_instance = KeyBufferManager(parsed_secret_spell=spell_sequence)
        return test_manager_instance

    def create_test_access_state():
        return test_access_state_instance

    def create_test_successful_spell_ips_state():
        return test_successful_spell_ips_instance

    # Override the dependencies for testing
    app.dependency_overrides[get_key_buffer_manager] = create_custom_key_buffer_manager
    app.dependency_overrides[get_user_access_state] = create_test_access_state
    app.dependency_overrides[get_successful_spell_ips_state] = (
        create_test_successful_spell_ips_state
    )

    client = TestClient(app)
    yield client

    # Clean up dependency overrides after test
    app.dependency_overrides.clear()


@pytest.fixture
def test_client_with_spell(simple_spell, sqlite_engine):
    """Create a test client with a specific spell sequence."""
    # Create singleton instances for this test
    test_manager_instance = None
    test_access_state_instance = UserAccessState(sqlite_engine)
    test_successful_spell_ips_instance = SuccessfulSpellIPsState(sqlite_engine)

    def create_spell_manager():
        nonlocal test_manager_instance
        if test_manager_instance is None:
            test_manager_instance = KeyBufferManager(parsed_secret_spell=simple_spell)
        return test_manager_instance

    def create_test_access_state():
        return test_access_state_instance

    def create_test_successful_spell_ips_state():
        return test_successful_spell_ips_instance

    # Override dependencies with test-specific implementations
    app.dependency_overrides[get_key_buffer_manager] = create_spell_manager
    app.dependency_overrides[get_user_access_state] = create_test_access_state
    app.dependency_overrides[get_successful_spell_ips_state] = (
        create_test_successful_spell_ips_state
    )

    client = TestClient(app)
    yield client

    # Clean up after test
    app.dependency_overrides.clear()


@pytest.fixture
def test_client_with_proxy_spell(simple_spell, sqlite_engine):
    """Create a test client with `X-Forwarded-For` client IP resolution."""
    # Create singleton instances for this test
    test_manager_instance = None
    test_access_state_instance = UserAccessState(sqlite_engine)
    test_successful_spell_ips_instance = SuccessfulSpellIPsState(sqlite_engine)

    def create_spell_manager():
        nonlocal test_manager_instance
        if test_manager_instance is None:
            test_manager_instance = KeyBufferManager(parsed_secret_spell=simple_spell)
        return test_manager_instance

    def create_test_access_state():
        return test_access_state_instance

    def create_test_successful_spell_ips_state():
        return test_successful_spell_ips_instance

    # Override dependencies with test-specific implementations
    app.dependency_overrides[get_key_buffer_manager] = create_spell_manager
    app.dependency_overrides[get_user_access_state] = create_test_access_state
    app.dependency_overrides[get_successful_spell_ips_state] = (
        create_test_successful_spell_ips_state
    )

    # Wrap app with ProxyHeadersMiddleware to allow X-Forwarded-For to set request.client.host
    proxied_app = ProxyHeadersMiddleware(app, trusted_hosts="*")
    client = TestClient(proxied_app)
    yield client

    # Clean up after test
    app.dependency_overrides.clear()


@pytest.fixture(autouse=True)
def reset_dependency_overrides():
    """Ensure dependency overrides are cleared between tests."""
    yield
    # Clean up any remaining dependency overrides
    app.dependency_overrides.clear()


@pytest.fixture
def mock_env_no_spell():
    """Mock environment with no spell configured."""
    with patch.dict(os.environ, {"APP_SECRET_SPELL": ""}, clear=False):
        yield


@pytest.fixture
def mock_env_custom_spell():
    """Mock environment with custom spell."""
    with patch.dict(os.environ, {"APP_SECRET_SPELL": "x,y,z"}, clear=False):
        yield
