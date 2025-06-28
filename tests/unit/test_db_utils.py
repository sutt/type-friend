import pytest
from unittest.mock import patch
from app.db_utils import list_ips, erase_ip
from app.database import get_session, SuccessfulSpellIP, init_db, reset_engine

@pytest.fixture(autouse=True)
def setup_teardown_module(dburl_env):
    """Create the database and table for the tests and tear it down after."""
    init_db()
    yield
    reset_engine()


def test_list_ips_empty_table(capsys):
    """Test list_ips with an empty table."""
    list_ips()
    captured = capsys.readouterr()
    assert "No IPs found" in captured.out

def test_list_ips_with_data(capsys):
    """Test list_ips with data in the table."""
    session = get_session()
    session.add(SuccessfulSpellIP(ip="192.168.1.1", user_uuid="test-uuid-1"))
    session.add(SuccessfulSpellIP(ip="192.168.1.2", user_uuid="test-uuid-2"))
    session.commit()
    session.close()

    list_ips()
    captured = capsys.readouterr()
    assert "192.168.1.1" in captured.out
    assert "test-uuid-1" in captured.out
    assert "192.168.1.2" in captured.out
    assert "test-uuid-2" in captured.out

def test_erase_ip_existing_ip(capsys):
    """Test erase_ip with an existing IP."""
    session = get_session()
    session.add(SuccessfulSpellIP(ip="192.168.1.3", user_uuid="test-uuid-3"))
    session.commit()
    session.close()

    erase_ip("192.168.1.3")
    captured = capsys.readouterr()
    assert "Successfully erased IP address: 192.168.1.3" in captured.out

    # Verify the IP is gone
    session = get_session()
    record = session.query(SuccessfulSpellIP).filter_by(ip="192.168.1.3").first()
    session.close()
    assert record is None

def test_erase_ip_nonexistent_ip(capsys):
    """Test erase_ip with a nonexistent IP."""
    erase_ip("192.168.1.4")
    captured = capsys.readouterr()
    assert "IP address not found: 192.168.1.4" in captured.out
