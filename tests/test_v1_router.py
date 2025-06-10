import tests.env_setup
import pytest
from unittest.mock import patch, MagicMock
from fastapi import FastAPI
from fastapi.testclient import TestClient

from routers.v1 import router


@pytest.fixture
def app():
    app = FastAPI()
    app.include_router(router)
    return app


@pytest.fixture
def client(app):
    return TestClient(app)


class TestV1Router:
    @patch('routers.v1.get_secret')
    def test_read_secret(self, mock_get_secret, client):
        # Arrange
        mock_get_secret.return_value = {"username": "test_user", "password": "test_password"}

        # Create a test request with the necessary state
        app = client.app

        @app.middleware("http")
        async def add_test_state(request, call_next):
            request.state.entity_uuid = "test-entity"
            request.state.licence_uuid = "test-license"
            response = await call_next(request)
            return response

        # Act
        response = client.get("/credential/v1/test-service")

        # Assert
        assert response.status_code == 200
        assert response.json() == {"username": "test_user", "password": "test_password"}
        mock_get_secret.assert_called_once_with("test-entity", "test-license", "test-service")

    @patch('routers.v1.create_secret')
    def test_create_new_secret(self, mock_create_secret, client):
        # Arrange
        mock_create_secret.return_value = {"message": "Secret recorded successfully"}
        secret_data = {"username": "new_user", "password": "new_password"}

        # Create a test request with the necessary state
        app = client.app

        @app.middleware("http")
        async def add_test_state(request, call_next):
            request.state.entity_uuid = "test-entity"
            response = await call_next(request)
            return response

        # Act
        response = client.post(
            "/credential/v1/test-license/test-service",
            json=secret_data
        )

        # Assert
        assert response.status_code == 200
        assert response.json() == {"message": "Secret recorded successfully"}
        mock_create_secret.assert_called_once_with(
            "test-entity", "test-license", "test-service", secret_data
        )
