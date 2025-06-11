import os
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch

# Import your app components
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'app'))

from main import app, key_buffer_manager, user_access_granted
from key_buffer_manager import KeyBufferManager


@pytest.fixture
def test_client():
    """Create a test client for FastAPI app."""
    return TestClient(app)


@pytest.fixture
def simple_spell():
    """Simple spell sequence for testing."""
    return ["a", "b", "Enter"]


@pytest.fixture
def konami_code_spell():
    """The actual Konami code from .env.example."""
    return ["ArrowUp", "ArrowUp", "ArrowDown", "ArrowDown", 
            "ArrowLeft", "ArrowRight", "ArrowLeft", "ArrowRight", 
            "b", "a", "Enter"]


@pytest.fixture
def clean_key_buffer_manager(simple_spell):
    """Create a fresh KeyBufferManager instance for each test."""
    return KeyBufferManager(parsed_secret_spell=simple_spell)


@pytest.fixture
def test_uuid():
    """Consistent UUID for testing."""
    return "test-uuid-12345"


@pytest.fixture(autouse=True)
def reset_global_state():
    """Reset global state before each test."""
    # Clear the user access granted dictionary
    user_access_granted.clear()
    # Clear all user buffers in the key buffer manager
    key_buffer_manager._user_key_buffers.clear()
    yield
    # Cleanup after test
    user_access_granted.clear()
    key_buffer_manager._user_key_buffers.clear()


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
