import tests.env_setup
import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from fastapi import HTTPException
from starlette.requests import Request
from starlette.responses import Response, JSONResponse
from datetime import datetime, timezone

from middlewares.licence_middleware import (
    extract_licence, 
    is_headers_licence_present, 
    check_headers_licence,
    is_licence_found,
    extract_entity,
    LicenceVerificationMiddleware,
    get_licences,
    filter_licences,
    prepare_licences,
    refresh_cache_token,
    refresh_licences,
    check_licence
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

    def test_is_licence_found_none(self):
        # Arrange
        mock_request = MagicMock()
        mock_request.state.licenses = None

        # Act
        result = is_licence_found(mock_request, "test-license")

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

    @patch('middlewares.licence_middleware.httpx')
    def test_get_licences_success(self, mock_httpx):
        # Arrange
        token = "test-token"
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"data": [{"uuid": "test-license"}]}
        mock_httpx.get.return_value = mock_response

        # Act
        result = get_licences(token)

        # Assert
        assert result == [{"uuid": "test-license"}]
        mock_httpx.get.assert_called_once()

    @patch('middlewares.licence_middleware.httpx')
    def test_get_licences_failure(self, mock_httpx):
        # Arrange
        token = "test-token"
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_httpx.get.return_value = mock_response

        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            get_licences(token)

        assert exc_info.value.status_code == 500
        assert exc_info.value.detail == "Licences request failed"

    def test_filter_licences_valid(self):
        # Arrange
        now = int(datetime.now(timezone.utc).timestamp())
        past = now - 3600  # 1 hour ago
        future = now + 3600  # 1 hour in the future

        licences = [
            {"uuid": "valid-license", "type_uuid": "type1", "name": "Valid License", 
             "iat": past, "exp": future, "entity_uuid": "entity1", 
             "api_roles": ["role1"], "app_roles": ["role2"], "apps": ["app1"]},
            {"uuid": "expired-license", "type_uuid": "type2", "name": "Expired License", 
             "iat": past, "exp": past, "entity_uuid": "entity2", 
             "api_roles": ["role3"], "app_roles": ["role4"], "apps": ["app2"]},
            {"uuid": "future-license", "type_uuid": "type3", "name": "Future License", 
             "iat": future, "exp": future + 3600, "entity_uuid": "entity3", 
             "api_roles": ["role5"], "app_roles": ["role6"], "apps": ["app3"]}
        ]

        # Act
        result = filter_licences(licences)

        # Assert
        assert len(result) == 1
        assert result[0]["uuid"] == "valid-license"

    def test_prepare_licences(self):
        # Arrange
        token = "test-token"

        # Act
        with patch('middlewares.licence_middleware.get_licences') as mock_get_licences, \
             patch('middlewares.licence_middleware.filter_licences') as mock_filter_licences:
            mock_get_licences.return_value = [{"uuid": "test-license"}]
            mock_filter_licences.return_value = [{"uuid": "filtered-license"}]

            result = prepare_licences(token)

        # Assert
        assert result == [{"uuid": "filtered-license"}]
        mock_get_licences.assert_called_once_with(token)
        mock_filter_licences.assert_called_once_with([{"uuid": "test-license"}])

    @patch('middlewares.licence_middleware.read_cache_token')
    def test_refresh_cache_token(self, mock_read_cache_token):
        # Arrange
        mock_request = MagicMock()
        mock_request.state.token = "test-token"
        mock_request.state.licenses = [{"uuid": "test-license"}]

        mock_read_cache_token.return_value = {"key": "value"}

        # Act
        result = refresh_cache_token(mock_request)

        # Assert
        assert result == {"key": "value", "licenses": [{"uuid": "test-license"}]}
        mock_read_cache_token.assert_called_once_with("test-token")

    @patch('middlewares.licence_middleware.prepare_licences')
    @patch('middlewares.licence_middleware.write_cache_token')
    @patch('middlewares.licence_middleware.refresh_cache_token')
    def test_refresh_licences(self, mock_refresh_cache_token, mock_write_cache_token, mock_prepare_licences):
        # Arrange
        mock_request = MagicMock()
        mock_request.state.token = "test-token"

        mock_prepare_licences.return_value = [{"uuid": "test-license"}]
        mock_refresh_cache_token.return_value = {"key": "value", "licenses": [{"uuid": "test-license"}]}

        # Act
        refresh_licences(mock_request)

        # Assert
        assert mock_request.state.licenses == [{"uuid": "test-license"}]
        mock_prepare_licences.assert_called_once_with("test-token")
        mock_refresh_cache_token.assert_called_once_with(mock_request)
        mock_write_cache_token.assert_called_once_with(token="test-token", cache_token={"key": "value", "licenses": [{"uuid": "test-license"}]})

    def test_check_licence_found(self):
        # Arrange
        mock_request = MagicMock()
        licence = "test-license"

        # Act
        with patch('middlewares.licence_middleware.is_licence_found') as mock_is_licence_found:
            mock_is_licence_found.return_value = True
            check_licence(mock_request, licence)

        # Assert
        mock_is_licence_found.assert_called_once_with(mock_request, licence)

    def test_check_licence_refresh_and_found(self):
        # Arrange
        mock_request = MagicMock()
        licence = "test-license"

        # Act
        with patch('middlewares.licence_middleware.is_licence_found') as mock_is_licence_found, \
             patch('middlewares.licence_middleware.refresh_licences') as mock_refresh_licences:
            mock_is_licence_found.side_effect = [False, True]
            check_licence(mock_request, licence)

        # Assert
        assert mock_is_licence_found.call_count == 2
        mock_refresh_licences.assert_called_once_with(mock_request)

    def test_check_licence_not_found(self):
        # Arrange
        mock_request = MagicMock()
        licence = "test-license"

        # Act & Assert
        with patch('middlewares.licence_middleware.is_licence_found') as mock_is_licence_found, \
             patch('middlewares.licence_middleware.refresh_licences') as mock_refresh_licences:
            mock_is_licence_found.return_value = False

            with pytest.raises(HTTPException) as exc_info:
                check_licence(mock_request, licence)

            assert exc_info.value.status_code == 403
            assert exc_info.value.detail == "Licence not found"

        assert mock_is_licence_found.call_count == 2
        mock_refresh_licences.assert_called_once_with(mock_request)


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

    @patch('middlewares.licence_middleware.is_unprotected_path')
    @patch('middlewares.licence_middleware.is_unlicensed_path')
    async def test_dispatch_unlicensed_path(self, mock_is_unlicensed_path, mock_is_unprotected_path):
        # Arrange
        mock_is_unprotected_path.return_value = False
        mock_is_unlicensed_path.return_value = True

        mock_app = MagicMock()
        middleware = LicenceVerificationMiddleware(mock_app)

        mock_request = MagicMock()
        mock_request.url.path = "/unlicensed-path"

        mock_call_next = AsyncMock()
        mock_response = Response(content="Test response")
        mock_call_next.return_value = mock_response

        # Act
        response = await middleware.dispatch(mock_request, mock_call_next)

        # Assert
        assert response == mock_response
        mock_call_next.assert_called_once_with(mock_request)

    @patch('middlewares.licence_middleware.is_unprotected_path')
    @patch('middlewares.licence_middleware.is_unlicensed_path')
    @patch('middlewares.licence_middleware.check_headers_licence')
    @patch('middlewares.licence_middleware.extract_licence')
    @patch('middlewares.licence_middleware.check_licence')
    @patch('middlewares.licence_middleware.extract_entity')
    async def test_dispatch_protected_path(self, mock_extract_entity, mock_check_licence, 
                                          mock_extract_licence, mock_check_headers_licence,
                                          mock_is_unlicensed_path, mock_is_unprotected_path):
        # Arrange
        mock_is_unprotected_path.return_value = False
        mock_is_unlicensed_path.return_value = False
        mock_extract_licence.return_value = "test-license"
        mock_extract_entity.return_value = "test-entity"

        mock_app = MagicMock()
        middleware = LicenceVerificationMiddleware(mock_app)

        mock_request = MagicMock()
        mock_request.url.path = "/protected-path"

        mock_call_next = AsyncMock()
        mock_response = Response(content="Test response")
        mock_call_next.return_value = mock_response

        # Act
        response = await middleware.dispatch(mock_request, mock_call_next)

        # Assert
        assert response == mock_response
        mock_check_headers_licence.assert_called_once_with(mock_request)
        mock_extract_licence.assert_called_once_with(mock_request)
        mock_check_licence.assert_called_once_with(mock_request, "test-license")
        assert mock_request.state.licence_uuid == "test-license"
        mock_extract_entity.assert_called_once_with(mock_request)
        assert mock_request.state.entity_uuid == "test-entity"
        mock_call_next.assert_called_once_with(mock_request)

    @patch('middlewares.licence_middleware.is_unprotected_path')
    @patch('middlewares.licence_middleware.is_unlicensed_path')
    async def test_dispatch_exception_handling(self, mock_is_unlicensed_path, mock_is_unprotected_path):
        # Arrange
        mock_is_unprotected_path.return_value = False
        mock_is_unlicensed_path.return_value = False

        mock_app = MagicMock()
        middleware = LicenceVerificationMiddleware(mock_app)

        mock_request = MagicMock()
        mock_request.url.path = "/protected-path"
        mock_request.headers = {}  # This will cause check_headers_licence to raise an exception

        mock_call_next = AsyncMock()

        # Act
        response = await middleware.dispatch(mock_request, mock_call_next)

        # Assert
        assert isinstance(response, JSONResponse)
        assert response.status_code == 403
        assert response.body == b'{"detail":"Licence header missing"}'
        mock_call_next.assert_not_called()
