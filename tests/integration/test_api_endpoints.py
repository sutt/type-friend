import pytest
from unittest.mock import patch
from fastapi.testclient import TestClient


class TestRootEndpoint:
    """Tests for the root endpoint that serves the HTML page."""
    
    def test_get_root_returns_html(self, test_client):
        """Test that root endpoint returns HTML page."""
        response = test_client.get("/")
        
        assert response.status_code == 200
        assert response.headers["content-type"] == "text/html; charset=utf-8"
        assert "KeyPress Event Tracker" in response.text
        assert "protected-link" in response.text


class TestKeypressEndpoint:
    """Tests for the keypress endpoint."""
    
    def test_keypress_single_key(self, test_client, test_uuid):
        """Test sending a single keypress."""
        payload = {"key": "a", "uuid": test_uuid}
        response = test_client.post("/keypress", json=payload)
        
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Key 'a' received"
        assert data["spell_successful"] is False
    
    def test_keypress_complete_spell_sequence(self, test_client_with_spell, test_uuid, simple_spell):
        """Test completing the spell sequence triggers success."""
        responses = []
        for key in simple_spell:
            payload = {"key": key, "uuid": test_uuid}
            response = test_client_with_spell.post("/keypress", json=payload)
            responses.append(response.json())
        
        # XXX: Last response should indicate spell success
        final_response = responses[-1]
        assert final_response["spell_successful"] is True
        assert "Spell cast successfully!" in final_response["message"]
    
    def test_keypress_invalid_payload(self, test_client):
        """Test keypress with missing required fields."""
        # Missing 'uuid' field
        payload = {"key": "a"}
        response = test_client.post("/keypress", json=payload)
        
        assert response.status_code == 422  # Validation error
    
    def test_keypress_multiple_users(self, test_client):
        """Test that different users have isolated spell progress."""
        user1 = "uuid-user-1"
        user2 = "uuid-user-2"
        
        # XXX: User 1 starts spell sequence
        payload1 = {"key": "ArrowUp", "uuid": user1}
        response1 = test_client.post("/keypress", json=payload1)
        assert response1.json()["spell_successful"] is False
        
        # XXX: User 2 presses different key
        payload2 = {"key": "x", "uuid": user2}
        response2 = test_client.post("/keypress", json=payload2)
        assert response2.json()["spell_successful"] is False
        
        # XXX: Users should have independent progress
        assert response1.status_code == 200
        assert response2.status_code == 200


class TestProtectedResourceEndpoint:
    """Tests for the protected resource endpoint."""
    
    def test_protected_resource_no_session_id(self, test_client):
        """Test accessing protected resource without session_id."""
        response = test_client.get("/protected_resource")
        
        assert response.status_code == 401
        assert response.json()["detail"] == "Session ID required"
    
    def test_protected_resource_invalid_session_id(self, test_client):
        """Test accessing protected resource with invalid session_id."""
        response = test_client.get("/protected_resource?session_id=invalid-uuid")
        
        assert response.status_code == 403
        assert response.json()["detail"] == "Access denied. Cast the secret spell correctly."
    
    def test_protected_resource_valid_access(self, test_client_with_custom_spell, test_uuid):
        """Test accessing protected resource after casting spell."""
        # XXX: Cast the custom spell sequence (x, y, z)
        keys = ['x', 'y', 'z']
        
        for key in keys:
            payload = {"key": key, "uuid": test_uuid}
            test_client_with_custom_spell.post("/keypress", json=payload)
        
        # XXX: Now access the protected resource
        response = test_client_with_custom_spell.get(f"/protected_resource?session_id={test_uuid}")
        
        assert response.status_code == 200
        data = response.json()
        assert "Welcome to the protected resource!" in data["message"]
        assert "You cast the spell correctly." in data["message"]


class TestEnvironmentConfiguration:
    """Tests demonstrating environment variable configuration."""
    
    def test_custom_spell_from_dependency_injection(self, test_client_with_custom_spell, test_uuid):
        """Test that custom spell from dependency injection works."""
        # XXX: Try the custom spell sequence
        keys = ["x", "y", "z"]
        responses = []
        
        for key in keys:
            payload = {"key": key, "uuid": test_uuid}
            response = test_client_with_custom_spell.post("/keypress", json=payload)
            responses.append(response.json())
        
        # XXX: All but the last should be false, last should be true
        assert all(r["spell_successful"] is False for r in responses[:-1])
        assert responses[-1]["spell_successful"] is True
    
    def test_empty_spell_configuration(self, test_uuid):
        """Test behavior with empty spell configuration."""
        from main import app, get_key_buffer_manager, get_user_access_state
        from key_buffer_manager import KeyBufferManager
        
        # XXX: Create singleton instances for this test
        test_manager_instance = None
        test_access_state_instance = {}
        
        # XXX: Override with empty spell
        def create_empty_spell_manager():
            nonlocal test_manager_instance
            if test_manager_instance is None:
                test_manager_instance = KeyBufferManager(parsed_secret_spell=[])
            return test_manager_instance
        
        def create_test_access_state():
            return test_access_state_instance
        
        app.dependency_overrides[get_key_buffer_manager] = create_empty_spell_manager
        app.dependency_overrides[get_user_access_state] = create_test_access_state
        
        client = TestClient(app)
        
        try:
            # XXX: With empty spell, no sequence should trigger success
            payload = {"key": "a", "uuid": test_uuid}
            response = client.post("/keypress", json=payload)
            
            assert response.status_code == 200
            assert response.json()["spell_successful"] is False
        finally:
            # XXX: Clean up
            app.dependency_overrides.clear()


class TestEndToEndFlow:
    """End-to-end integration tests."""
    
    def test_complete_user_journey(self, test_client_with_spell, simple_spell):
        """Test complete user journey from keypress to protected access."""
        user_uuid = "e2e-test-uuid"
        
        # XXX: Step 1: User loads the page (implicitly tested by other tests)
        root_response = test_client_with_spell.get("/")
        assert root_response.status_code == 200
        
        # XXX: Step 2: User presses keys to cast spell
        spell_successful = False
        for key in simple_spell:
            payload = {"key": key, "uuid": user_uuid}
            response = test_client_with_spell.post("/keypress", json=payload)
            assert response.status_code == 200
            
            if response.json().get("spell_successful"):
                spell_successful = True
        
        # XXX: Step 3: Verify spell was cast successfully
        assert spell_successful, "Spell should have been cast successfully"
        
        # XXX: Step 4: Access protected resource
        protected_response = test_client_with_spell.get(f"/protected_resource?session_id={user_uuid}")
        assert protected_response.status_code == 200
        assert "Welcome to the protected resource!" in protected_response.json()["message"]
    
    def test_user_without_spell_cannot_access_protected(self, test_client):
        """Test that user who hasn't cast spell cannot access protected resource."""
        user_uuid = "no-spell-uuid"
        
        # XXX: User presses some keys but not the correct spell
        wrong_keys = ["a", "b", "c"]
        for key in wrong_keys:
            payload = {"key": key, "uuid": user_uuid}
            response = test_client.post("/keypress", json=payload)
            assert response.json()["spell_successful"] is False
        
        # XXX: Try to access protected resource
        protected_response = test_client.get(f"/protected_resource?session_id={user_uuid}")
        assert protected_response.status_code == 403
        assert "Access denied" in protected_response.json()["detail"]
