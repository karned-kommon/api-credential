import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from fastapi import HTTPException
from starlette.requests import Request
from starlette.responses import Response

from middlewares.licence_middleware import (
    extract_licence, 
    is_headers_licence_present, 
    check_headers_licence,
    is_licence_found,
    extract_entity,
    LicenceVerificationMiddleware
)


class TestLicenceMiddlewareFunctions:
    def test_extract_licence(self):
        # Arrange
        mock_request = MagicMock()
        mock_request.headers = {"X-License-Key": "test-license-key"}
        
        # Act
        result = extract_licence(mock_request)
        
        # Assert
        assert result == "test-license-key"
    
    def test_is_headers_licence_present_true(self):
        # Arrange
        mock_request = MagicMock()
        mock_request.headers = {"X-License-Key": "test-license-key"}
        
        # Act
        result = is_headers_licence_present(mock_request)
        
        # Assert
        assert result is True
    
    def test_is_headers_licence_present_false(self):
        # Arrange
        mock_request = MagicMock()
        mock_request.headers = {}
        
        # Act
        result = is_headers_licence_present(mock_request)
        
        # Assert
        assert result is False
    
    def test_check_headers_licence_success(self):
        # Arrange
        mock_request = MagicMock()
        mock_request.headers = {"X-License-Key": "test-license-key"}
        
        # Act & Assert
        # Should not raise an exception
        check_headers_licence(mock_request)
    
    def test_check_headers_licence_failure(self):
        # Arrange
        mock_request = MagicMock()
        mock_request.headers = {}
        
        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            check_headers_licence(mock_request)
        
        assert exc_info.value.status_code == 403
        assert exc_info.value.detail == "Licence header missing"
    
    def test_is_licence_found_true(self):
        # Arrange
        mock_request = MagicMock()
        mock_request.state.licenses = [
            {"uuid": "test-license-1", "name": "License 1"},
            {"uuid": "test-license-2", "name": "License 2"}
        ]
        
        # Act
        result = is_licence_found(mock_request, "test-license-2")
        
        # Assert
        assert result is True
    
    def test_is_licence_found_false(self):
        # Arrange
        mock_request = MagicMock()
        mock_request.state.licenses = [
            {"uuid": "test-license-1", "name": "License 1"},
            {"uuid": "test-license-2", "name": "License 2"}
        ]
        
        # Act
        result = is_licence_found(mock_request, "non-existent-license")
        
        # Assert
        assert result is False
    
    def test_extract_entity_success(self):
        # Arrange
        mock_request = MagicMock()
        mock_request.state.licence_uuid = "test-license-2"
        mock_request.state.licenses = [
            {"uuid": "test-license-1", "entity_uuid": "entity-1"},
            {"uuid": "test-license-2", "entity_uuid": "entity-2"}
        ]
        
        # Act
        result = extract_entity(mock_request)
        
        # Assert
        assert result == "entity-2"
    
    def test_extract_entity_not_found(self):
        # Arrange
        mock_request = MagicMock()
        mock_request.state.licence_uuid = "non-existent-license"
        mock_request.state.licenses = [
            {"uuid": "test-license-1", "entity_uuid": "entity-1"},
            {"uuid": "test-license-2", "entity_uuid": "entity-2"}
        ]
        
        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            extract_entity(mock_request)
        
        assert exc_info.value.status_code == 500
        assert exc_info.value.detail == "Entity not found"


@pytest.mark.asyncio
class TestLicenceVerificationMiddleware:
    @patch('middlewares.licence_middleware.is_unprotected_path')
    @patch('middlewares.licence_middleware.is_unlicensed_path')
    async def test_dispatch_unprotected_path(self, mock_is_unlicensed_path, mock_is_unprotected_path):
        # Arrange
        mock_is_unprotected_path.return_value = True
        mock_is_unlicensed_path.return_value = False
        
        mock_app = MagicMock()
        middleware = LicenceVerificationMiddleware(mock_app)
        
        mock_request = MagicMock()
        mock_request.url.path = "/docs"
        
        mock_call_next = AsyncMock()
        mock_response = Response(content="Test response")
        mock_call_next.return_value = mock_response
        
        # Act
        response = await middleware.dispatch(mock_request, mock_call_next)
        
        # Assert
        assert response == mock_response
        mock_call_next.assert_called_once_with(mock_request)