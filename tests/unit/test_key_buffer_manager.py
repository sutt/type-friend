import pytest
from app.key_buffer_manager import KeyBufferManager


class TestKeyBufferManager:
    """Unit tests for KeyBufferManager class."""
    
    def test_init_with_valid_spell(self, simple_spell):
        """Test initialization with a valid spell sequence."""
        manager = KeyBufferManager(parsed_secret_spell=simple_spell)
        
        assert manager._parsed_secret_spell == simple_spell
        assert manager._spell_key_count == 3
        assert manager._user_key_buffers == {}
    
    def test_init_with_empty_spell(self):
        """Test initialization with empty spell."""
        manager = KeyBufferManager(parsed_secret_spell=[])
        
        assert manager._parsed_secret_spell == []
        assert manager._spell_key_count == 0
    
    def test_add_key_new_user(self, clean_key_buffer_manager, test_uuid):
        """Test adding key for new user creates buffer."""
        result = clean_key_buffer_manager.add_key(test_uuid, "a")
        
        assert result == ["a"]
        assert clean_key_buffer_manager.get_buffer(test_uuid) == ["a"]
    
    def test_add_key_buffer_trimming(self, clean_key_buffer_manager, test_uuid):
        """Test buffer is trimmed to spell length."""
        # Add more keys than spell length (spell is ["a", "b", "Enter"])
        clean_key_buffer_manager.add_key(test_uuid, "x")
        clean_key_buffer_manager.add_key(test_uuid, "y")
        clean_key_buffer_manager.add_key(test_uuid, "z")
        clean_key_buffer_manager.add_key(test_uuid, "a")
        result = clean_key_buffer_manager.add_key(test_uuid, "b")
        
        # Should only keep last 3 keys (spell length)
        assert result == ["z", "a", "b"]
    
    def test_add_key_zero_spell_length(self, test_uuid):
        """Test buffer behavior with zero-length spell."""
        manager = KeyBufferManager(parsed_secret_spell=[])
        
        result = manager.add_key(test_uuid, "a")
        
        # Buffer should be empty when spell length is 0
        assert result == []
    
    def test_check_spell_exact_match(self, clean_key_buffer_manager, test_uuid):
        """Test spell check with exact case-sensitive match."""
        spell = ["a", "b", "Enter"]
        
        # Add exact spell sequence
        for key in spell:
            clean_key_buffer_manager.add_key(test_uuid, key)
        
        assert clean_key_buffer_manager.check_spell(test_uuid) is True
    
    def test_check_spell_case_insensitive(self, clean_key_buffer_manager, test_uuid):
        """Test spell check is case-insensitive."""
        # Add spell with different case
        clean_key_buffer_manager.add_key(test_uuid, "A")
        clean_key_buffer_manager.add_key(test_uuid, "B")
        clean_key_buffer_manager.add_key(test_uuid, "enter")
        
        assert clean_key_buffer_manager.check_spell(test_uuid) is True
    
    def test_check_spell_partial_sequence(self, clean_key_buffer_manager, test_uuid):
        """Test spell check fails with partial sequence."""
        # Add only part of the spell
        clean_key_buffer_manager.add_key(test_uuid, "a")
        clean_key_buffer_manager.add_key(test_uuid, "b")
        
        assert clean_key_buffer_manager.check_spell(test_uuid) is False
    
    def test_check_spell_wrong_sequence(self, clean_key_buffer_manager, test_uuid):
        """Test spell check fails with wrong sequence."""
        # Add wrong sequence
        clean_key_buffer_manager.add_key(test_uuid, "a")
        clean_key_buffer_manager.add_key(test_uuid, "c")
        clean_key_buffer_manager.add_key(test_uuid, "Enter")
        
        assert clean_key_buffer_manager.check_spell(test_uuid) is False
    
    def test_check_spell_empty_spell(self, test_uuid):
        """Test spell check with empty spell always returns False."""
        manager = KeyBufferManager(parsed_secret_spell=[])
        
        manager.add_key(test_uuid, "a")
        
        assert manager.check_spell(test_uuid) is False
    
    def test_multiple_users_isolation(self, clean_key_buffer_manager):
        """Test that different users have isolated buffers."""
        user1 = "uuid-1"
        user2 = "uuid-2"
        
        # User 1 adds correct spell
        clean_key_buffer_manager.add_key(user1, "a")
        clean_key_buffer_manager.add_key(user1, "b")
        clean_key_buffer_manager.add_key(user1, "Enter")
        
        # User 2 adds different keys
        clean_key_buffer_manager.add_key(user2, "x")
        clean_key_buffer_manager.add_key(user2, "y")
        clean_key_buffer_manager.add_key(user2, "z")
        
        assert clean_key_buffer_manager.check_spell(user1) is True
        assert clean_key_buffer_manager.check_spell(user2) is False
        assert clean_key_buffer_manager.get_buffer(user1) == ["a", "b", "Enter"]
        assert clean_key_buffer_manager.get_buffer(user2) == ["x", "y", "z"]
    
    def test_get_buffer_nonexistent_user(self, clean_key_buffer_manager):
        """Test getting buffer for user that doesn't exist."""
        result = clean_key_buffer_manager.get_buffer("nonexistent-uuid")
        assert result == []
