import os
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch

# XXX: Import your app components
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'app'))

from main import app, key_buffer_manager, user_access_granted
from key_buffer_manager import KeyBufferManager


@pytest.fixture
def test_client():
    """XXX: Create a test client for FastAPI app."""
    return TestClient(app)


@pytest.fixture
def simple_spell():
    """XXX: Simple spell sequence for testing."""
    return ["a", "b", "Enter"]


@pytest.fixture
def konami_code_spell():
    """XXX: The actual Konami code from .env.example."""
    return ["ArrowUp", "ArrowUp", "ArrowDown", "ArrowDown", 
            "ArrowLeft", "ArrowRight", "ArrowLeft", "ArrowRight", 
            "b", "a", "Enter"]


@pytest.fixture
def clean_key_buffer_manager(simple_spell):
    """XXX: Create a fresh KeyBufferManager instance for each test."""
    return KeyBufferManager(parsed_secret_spell=simple_spell)


@pytest.fixture
def test_uuid():
    """XXX: Consistent UUID for testing."""
    return "test-uuid-12345"


@pytest.fixture(autouse=True)
def reset_global_state():
    """XXX: Reset global state before each test."""
    # XXX: Clear the user access granted dictionary
    user_access_granted.clear()
    # XXX: Clear all user buffers in the key buffer manager
    key_buffer_manager._user_key_buffers.clear()
    yield
    # XXX: Cleanup after test
    user_access_granted.clear()
    key_buffer_manager._user_key_buffers.clear()


@pytest.fixture
def mock_env_no_spell():
    """XXX: Mock environment with no spell configured."""
    with patch.dict(os.environ, {"APP_SECRET_SPELL": ""}, clear=False):
        yield


@pytest.fixture
def mock_env_custom_spell():
    """XXX: Mock environment with custom spell."""
    with patch.dict(os.environ, {"APP_SECRET_SPELL": "x,y,z"}, clear=False):
        yield
