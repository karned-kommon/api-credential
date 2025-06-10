import tests.env_setup
import pytest
from unittest.mock import patch, MagicMock
from fastapi import HTTPException

from services.items_service import get_secret, create_secret


@pytest.fixture
def mock_hvac_client():
    with patch('services.items_service.client') as mock_client:
        yield mock_client


class TestItemsService:
    def test_get_secret_success(self, mock_hvac_client):
        # Arrange
        entity_uuid = "test-entity"
        licence_uuid = "test-license"
        service = "test-service"
        expected_data = {"username": "test_user", "password": "test_password"}

        mock_response = {
            "data": {
                "data": expected_data
            }
        }
        mock_hvac_client.secrets.kv.v2.read_secret_version.return_value = mock_response

        # Act
        result = get_secret(entity_uuid, licence_uuid, service)

        # Assert
        assert result == expected_data
        mock_hvac_client.secrets.kv.v2.read_secret_version.assert_called_once()

    def test_get_secret_not_found(self, mock_hvac_client):
        # Arrange
        from hvac.exceptions import InvalidPath

        entity_uuid = "test-entity"
        licence_uuid = "test-license"
        service = "nonexistent-service"

        mock_hvac_client.secrets.kv.v2.read_secret_version.side_effect = InvalidPath("Secret not found")

        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            get_secret(entity_uuid, licence_uuid, service)

        assert exc_info.value.status_code == 404
        assert exc_info.value.detail == "Secret not found"

    def test_get_secret_general_exception(self, mock_hvac_client):
        # Arrange
        entity_uuid = "test-entity"
        licence_uuid = "test-license"
        service = "test-service"

        mock_hvac_client.secrets.kv.v2.read_secret_version.side_effect = Exception("Vault general error")

        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            get_secret(entity_uuid, licence_uuid, service)

        assert exc_info.value.status_code == 500
        assert exc_info.value.detail == "Vault general error"

    def test_create_secret_success(self, mock_hvac_client):
        # Arrange
        entity_uuid = "test-entity"
        license_uuid = "test-license"
        service = "test-service"
        secret_data = {"username": "new_user", "password": "new_password"}

        # Act
        result = create_secret(entity_uuid, license_uuid, service, secret_data)

        # Assert
        assert result == {"message": "Secret recorded successfully"}
        mock_hvac_client.secrets.kv.v2.create_or_update_secret.assert_called_once()

    def test_create_secret_error(self, mock_hvac_client):
        # Arrange
        entity_uuid = "test-entity"
        license_uuid = "test-license"
        service = "test-service"
        secret_data = {"username": "new_user", "password": "new_password"}

        mock_hvac_client.secrets.kv.v2.create_or_update_secret.side_effect = Exception("Vault error")

        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            create_secret(entity_uuid, license_uuid, service, secret_data)

        assert exc_info.value.status_code == 500
        assert exc_info.value.detail == "Vault error"
