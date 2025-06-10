import tests.env_setup
import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
import main


class TestMain:
    def test_app_initialization(self):
        # Test that the FastAPI app is initialized correctly
        assert main.app is not None
        assert main.app.title == "FastAPI"
        assert main.app.openapi_url == "/credential/openapi.json"

    def test_custom_openapi_no_cached_schema(self):
        # Test that the custom OpenAPI schema is generated correctly when there's no cached schema
        with patch('main.get_openapi') as mock_get_openapi:
            mock_schema = {
                "components": {},
                "paths": {
                    "/test": {
                        "get": {}
                    }
                }
            }
            mock_get_openapi.return_value = mock_schema

            # Clear the cached schema
            main.app.openapi_schema = None

            # Get the schema
            schema = main.custom_openapi()

            # Verify the schema was modified correctly
            assert "securitySchemes" in schema["components"]
            assert "BearerAuth" in schema["components"]["securitySchemes"]
            assert "LicenceHeader" in schema["components"]["securitySchemes"]
            assert schema["paths"]["/test"]["get"]["security"] == [
                {"BearerAuth": []},
                {"LicenceHeader": []}
            ]

    def test_custom_openapi_cached_schema(self):
        # Test that the custom OpenAPI function returns the cached schema if it exists
        # Set a cached schema
        mock_schema = {"test": "cached_schema"}
        main.app.openapi_schema = mock_schema

        # Get the schema
        schema = main.custom_openapi()

        # Verify the cached schema was returned
        assert schema == mock_schema

        # Reset the cached schema for other tests
        main.app.openapi_schema = None
