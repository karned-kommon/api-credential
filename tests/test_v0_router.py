import tests.env_setup
import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from hvac.exceptions import InvalidPath
from routers.v0 import app, SecretRequest


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def mock_hvac_client():
    with patch('routers.v0.client') as mock_client:
        yield mock_client


class TestV0Router:
    def test_create_secret_new(self, client, mock_hvac_client):
        # Arrange
        mock_hvac_client.secrets.kv.v2.read_secret_version.side_effect = InvalidPath("Secret not found")
        
        # Act
        response = client.post(
            "/secret",
            json={"service": "test-service", "data": {"username": "test_user", "password": "test_password"}}
        )
        
        # Assert
        assert response.status_code == 200
        assert response.json() == {"message": "Secret created successfully"}
        mock_hvac_client.secrets.kv.v2.create_or_update_secret.assert_called_once()
    
    def test_create_secret_existing(self, client, mock_hvac_client):
        # Arrange
        mock_response = {
            "data": {
                "data": {"username": "existing_user", "password": "existing_password"}
            }
        }
        mock_hvac_client.secrets.kv.v2.read_secret_version.return_value = mock_response
        
        # Act
        response = client.post(
            "/secret",
            json={"service": "test-service", "data": {"username": "test_user", "password": "test_password"}}
        )
        
        # Assert
        assert response.status_code == 200
        assert response.json() == {
            "message": "Secret already exists",
            "data": {"username": "existing_user", "password": "existing_password"}
        }
        mock_hvac_client.secrets.kv.v2.create_or_update_secret.assert_not_called()
    
    def test_create_secret_error(self, client, mock_hvac_client):
        # Arrange
        mock_hvac_client.secrets.kv.v2.read_secret_version.side_effect = Exception("Vault error")
        
        # Act
        response = client.post(
            "/secret",
            json={"service": "test-service", "data": {"username": "test_user", "password": "test_password"}}
        )
        
        # Assert
        assert response.status_code == 500
        assert response.json() == {"detail": "Vault error"}
    
    def test_get_secret_success(self, client, mock_hvac_client):
        # Arrange
        mock_response = {
            "data": {
                "data": {"username": "test_user", "password": "test_password"}
            }
        }
        mock_hvac_client.secrets.kv.v2.read_secret_version.return_value = mock_response
        
        # Act
        response = client.get("/secret/test-service")
        
        # Assert
        assert response.status_code == 200
        assert response.json() == {"data": {"username": "test_user", "password": "test_password"}}
    
    def test_get_secret_not_found(self, client, mock_hvac_client):
        # Arrange
        mock_hvac_client.secrets.kv.v2.read_secret_version.side_effect = InvalidPath("Secret not found")
        
        # Act
        response = client.get("/secret/nonexistent-service")
        
        # Assert
        assert response.status_code == 404
        assert response.json() == {"detail": "Secret not found"}
    
    def test_get_secret_error(self, client, mock_hvac_client):
        # Arrange
        mock_hvac_client.secrets.kv.v2.read_secret_version.side_effect = Exception("Vault error")
        
        # Act
        response = client.get("/secret/test-service")
        
        # Assert
        assert response.status_code == 500
        assert response.json() == {"detail": "Vault error"}