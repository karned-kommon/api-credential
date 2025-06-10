import tests.env_setup
import pytest
import time
from unittest.mock import patch, MagicMock, AsyncMock
from fastapi import HTTPException
from starlette.requests import Request
from starlette.responses import Response, JSONResponse

from middlewares.token_middleware import (
    generate_state_info,
    is_token_valid_audience,
    is_token_active,
    read_cache_token,
    write_cache_token,
    introspect_token,
    prepare_cache_token,
    get_token_info,
    delete_cache_token,
    is_headers_token_present,
    extract_token,
    refresh_cache_token,
    store_token_info_in_state,
    check_headers_token,
    check_token,
    TokenVerificationMiddleware
)


class TestTokenMiddlewareFunctions:
    def test_generate_state_info(self):
        # Arrange
        token_info = {
            "sub": "user-123",
            "preferred_username": "test_user",
            "email": "test@example.com",
            "aud": "karned",
            "cached_time": 1234567890
        }

        # Act
        result = generate_state_info(token_info)

        # Assert
        assert result == {
            "user_uuid": "user-123",
            "user_display_name": "test_user",
            "user_email": "test@example.com",
            "user_audiences": "karned",
            "cached_time": 1234567890
        }

    def test_is_token_valid_audience_string_true(self):
        # Arrange
        token_info = {"aud": "karned"}

        # Act
        result = is_token_valid_audience(token_info)

        # Assert
        assert result is True

    def test_is_token_valid_audience_string_false(self):
        # Arrange
        token_info = {"aud": "other"}

        # Act
        result = is_token_valid_audience(token_info)

        # Assert
        assert result is False

    def test_is_token_valid_audience_list_true(self):
        # Arrange
        token_info = {"aud": ["karned", "other"]}

        # Act
        result = is_token_valid_audience(token_info)

        # Assert
        assert result is True

    def test_is_token_valid_audience_list_false(self):
        # Arrange
        token_info = {"aud": ["other1", "other2"]}

        # Act
        result = is_token_valid_audience(token_info)

        # Assert
        assert result is False

    def test_is_token_valid_audience_none(self):
        # Arrange
        token_info = {"aud": None}

        # Act
        result = is_token_valid_audience(token_info)

        # Assert
        assert result is False

    def test_is_token_active_true(self):
        # Arrange
        now = int(time.time())
        token_info = {
            "iat": now - 3600,  # 1 hour ago
            "exp": now + 3600   # 1 hour in the future
        }

        # Act
        result = is_token_active(token_info)

        # Assert
        assert result is True

    def test_is_token_active_expired(self):
        # Arrange
        now = int(time.time())
        token_info = {
            "iat": now - 7200,  # 2 hours ago
            "exp": now - 3600   # 1 hour ago
        }

        # Act
        result = is_token_active(token_info)

        # Assert
        assert result is False

    def test_is_token_active_not_yet_valid(self):
        # Arrange
        now = int(time.time())
        token_info = {
            "iat": now + 3600,  # 1 hour in the future
            "exp": now + 7200   # 2 hours in the future
        }

        # Act
        result = is_token_active(token_info)

        # Assert
        assert result is False

    def test_is_token_active_missing_fields(self):
        # Arrange
        token_info = {}

        # Act
        result = is_token_active(token_info)

        # Assert
        assert result is False

    @patch('middlewares.token_middleware.r')
    def test_read_cache_token_found(self, mock_redis):
        # Arrange
        token = "test-token"
        mock_redis.get.return_value = "{'key': 'value'}"

        # Act
        result = read_cache_token(token)

        # Assert
        assert result == {'key': 'value'}
        mock_redis.get.assert_called_once_with(token)

    @patch('middlewares.token_middleware.r')
    def test_read_cache_token_not_found(self, mock_redis):
        # Arrange
        token = "test-token"
        mock_redis.get.return_value = None

        # Act
        result = read_cache_token(token)

        # Assert
        assert result is None
        mock_redis.get.assert_called_once_with(token)

    @patch('middlewares.token_middleware.r')
    @patch('middlewares.token_middleware.time')
    def test_write_cache_token(self, mock_time, mock_redis):
        # Arrange
        token = "test-token"
        cache_token = {"key": "value", "exp": 1234567890}
        mock_time.time.return_value = 1234567000

        # Act
        write_cache_token(token, cache_token)

        # Assert
        mock_redis.set.assert_called_once_with(token, str(cache_token), ex=890)

    @patch('middlewares.token_middleware.r')
    @patch('middlewares.token_middleware.time')
    def test_write_cache_token_no_exp(self, mock_time, mock_redis):
        # Arrange
        token = "test-token"
        cache_token = {"key": "value"}

        # Act
        write_cache_token(token, cache_token)

        # Assert
        mock_redis.set.assert_not_called()

    @patch('middlewares.token_middleware.httpx')
    def test_introspect_token_success(self, mock_httpx):
        # Arrange
        token = "test-token"
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"active": True}
        mock_httpx.post.return_value = mock_response

        # Act
        result = introspect_token(token)

        # Assert
        assert result == {"active": True}
        mock_httpx.post.assert_called_once()

    @patch('middlewares.token_middleware.httpx')
    def test_introspect_token_failure(self, mock_httpx):
        # Arrange
        token = "test-token"
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_httpx.post.return_value = mock_response

        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            introspect_token(token)

        assert exc_info.value.status_code == 500
        assert exc_info.value.detail == "Keycloak introspection failed"
        mock_httpx.post.assert_called_once()

    @patch('middlewares.token_middleware.time')
    def test_prepare_cache_token(self, mock_time):
        # Arrange
        token_info = {"key": "value"}
        mock_time.time.return_value = 1234567890

        # Act
        result = prepare_cache_token(token_info)

        # Assert
        assert result == {"key": "value", "cached_time": 1234567890}

    @patch('middlewares.token_middleware.read_cache_token')
    def test_get_token_info_from_cache(self, mock_read_cache_token):
        # Arrange
        token = "test-token"
        mock_read_cache_token.return_value = {"active": True}

        # Act
        with patch('middlewares.token_middleware.introspect_token') as mock_introspect_token, \
             patch('middlewares.token_middleware.prepare_cache_token') as mock_prepare_cache_token, \
             patch('middlewares.token_middleware.write_cache_token') as mock_write_cache_token:
            result = get_token_info(token)

        # Assert
        assert result == {"active": True}
        mock_read_cache_token.assert_called_once_with(token)
        mock_introspect_token.assert_not_called()
        mock_prepare_cache_token.assert_not_called()
        mock_write_cache_token.assert_not_called()

    @patch('middlewares.token_middleware.read_cache_token')
    @patch('middlewares.token_middleware.introspect_token')
    @patch('middlewares.token_middleware.prepare_cache_token')
    @patch('middlewares.token_middleware.write_cache_token')
    def test_get_token_info_from_introspection(self, mock_write_cache_token, mock_prepare_cache_token, 
                                              mock_introspect_token, mock_read_cache_token):
        # Arrange
        token = "test-token"
        mock_read_cache_token.return_value = None
        mock_introspect_token.return_value = {"active": True}
        mock_prepare_cache_token.return_value = {"active": True, "cached_time": 1234567890}

        # Act
        result = get_token_info(token)

        # Assert
        assert result == {"active": True}
        mock_read_cache_token.assert_called_once_with(token)
        mock_introspect_token.assert_called_once_with(token)
        mock_prepare_cache_token.assert_called_once_with({"active": True})
        mock_write_cache_token.assert_called_once_with(token, {"active": True, "cached_time": 1234567890})

    @patch('middlewares.token_middleware.r')
    def test_delete_cache_token(self, mock_redis):
        # Arrange
        token = "test-token"

        # Act
        delete_cache_token(token)

        # Assert
        mock_redis.delete.assert_called_once_with(token)

    def test_is_headers_token_present_true(self):
        # Arrange
        mock_request = MagicMock()
        mock_request.headers = {"Authorization": "Bearer test-token"}

        # Act
        result = is_headers_token_present(mock_request)

        # Assert
        assert result is True

    def test_is_headers_token_present_no_header(self):
        # Arrange
        mock_request = MagicMock()
        mock_request.headers = {}

        # Act
        result = is_headers_token_present(mock_request)

        # Assert
        assert result is False

    def test_is_headers_token_present_invalid_format(self):
        # Arrange
        mock_request = MagicMock()
        mock_request.headers = {"Authorization": "Invalid test-token"}

        # Act
        result = is_headers_token_present(mock_request)

        # Assert
        assert result is False

    def test_extract_token(self):
        # Arrange
        mock_request = MagicMock()
        mock_request.headers = {"Authorization": "Bearer test-token"}

        # Act
        result = extract_token(mock_request)

        # Assert
        assert result == "test-token"

    @patch('middlewares.token_middleware.check_headers_token')
    @patch('middlewares.token_middleware.extract_token')
    @patch('middlewares.token_middleware.delete_cache_token')
    @patch('middlewares.token_middleware.get_token_info')
    @patch('middlewares.token_middleware.check_token')
    @patch('middlewares.token_middleware.generate_state_info')
    @patch('middlewares.token_middleware.store_token_info_in_state')
    def test_refresh_cache_token(self, mock_store_token_info_in_state, mock_generate_state_info, 
                                mock_check_token, mock_get_token_info, mock_delete_cache_token, 
                                mock_extract_token, mock_check_headers_token):
        # Arrange
        mock_request = MagicMock()
        mock_extract_token.return_value = "test-token"
        mock_get_token_info.return_value = {"active": True}
        mock_generate_state_info.return_value = {"user_uuid": "user-123"}

        # Act
        refresh_cache_token(mock_request)

        # Assert
        mock_check_headers_token.assert_called_once_with(mock_request)
        mock_extract_token.assert_called_once_with(mock_request)
        mock_delete_cache_token.assert_called_once_with("test-token")
        mock_get_token_info.assert_called_once_with("test-token")
        mock_check_token.assert_called_once_with({"active": True})
        mock_generate_state_info.assert_called_once_with({"active": True})
        mock_store_token_info_in_state.assert_called_once_with({"user_uuid": "user-123"}, mock_request)

    @patch('middlewares.token_middleware.extract_token')
    def test_store_token_info_in_state(self, mock_extract_token):
        # Arrange
        mock_request = MagicMock()
        state_token_info = {
            "user_uuid": "user-123",
            "user_display_name": "test_user",
            "user_email": "test@example.com",
            "user_audiences": "karned",
            "cached_time": 1234567890
        }
        mock_extract_token.return_value = "test-token"

        # Act
        store_token_info_in_state(state_token_info, mock_request)

        # Assert
        assert mock_request.state.token_info == state_token_info
        assert mock_request.state.user_uuid == "user-123"
        assert mock_request.state.token == "test-token"
        mock_extract_token.assert_called_once_with(mock_request)

    def test_check_headers_token_present(self):
        # Arrange
        mock_request = MagicMock()

        # Act
        with patch('middlewares.token_middleware.is_headers_token_present') as mock_is_headers_token_present:
            mock_is_headers_token_present.return_value = True
            check_headers_token(mock_request)

        # Assert
        mock_is_headers_token_present.assert_called_once_with(mock_request)

    def test_check_headers_token_missing(self):
        # Arrange
        mock_request = MagicMock()

        # Act & Assert
        with patch('middlewares.token_middleware.is_headers_token_present') as mock_is_headers_token_present:
            mock_is_headers_token_present.return_value = False
            
            with pytest.raises(HTTPException) as exc_info:
                check_headers_token(mock_request)
            
            assert exc_info.value.status_code == 401
            assert exc_info.value.detail == "Token manquant ou invalide"
        
        mock_is_headers_token_present.assert_called_once_with(mock_request)

    def test_check_token_valid(self):
        # Arrange
        token_info = {"active": True}

        # Act
        with patch('middlewares.token_middleware.is_token_active') as mock_is_token_active, \
             patch('middlewares.token_middleware.is_token_valid_audience') as mock_is_token_valid_audience:
            mock_is_token_active.return_value = True
            mock_is_token_valid_audience.return_value = True
            check_token(token_info)

        # Assert
        mock_is_token_active.assert_called_once_with(token_info)
        mock_is_token_valid_audience.assert_called_once_with(token_info)

    def test_check_token_inactive(self):
        # Arrange
        token_info = {"active": False}

        # Act & Assert
        with patch('middlewares.token_middleware.is_token_active') as mock_is_token_active:
            mock_is_token_active.return_value = False
            
            with pytest.raises(HTTPException) as exc_info:
                check_token(token_info)
            
            assert exc_info.value.status_code == 401
            assert exc_info.value.detail == "Token is not active"
        
        mock_is_token_active.assert_called_once_with(token_info)

    def test_check_token_invalid_audience(self):
        # Arrange
        token_info = {"active": True}

        # Act & Assert
        with patch('middlewares.token_middleware.is_token_active') as mock_is_token_active, \
             patch('middlewares.token_middleware.is_token_valid_audience') as mock_is_token_valid_audience:
            mock_is_token_active.return_value = True
            mock_is_token_valid_audience.return_value = False
            
            with pytest.raises(HTTPException) as exc_info:
                check_token(token_info)
            
            assert exc_info.value.status_code == 401
            assert exc_info.value.detail == "Token is not valid for this audience"
        
        mock_is_token_active.assert_called_once_with(token_info)
        mock_is_token_valid_audience.assert_called_once_with(token_info)


@pytest.mark.asyncio
class TestTokenVerificationMiddleware:
    @patch('middlewares.token_middleware.is_unprotected_path')
    async def test_dispatch_unprotected_path(self, mock_is_unprotected_path):
        # Arrange
        mock_is_unprotected_path.return_value = True

        mock_app = MagicMock()
        middleware = TokenVerificationMiddleware(mock_app)

        mock_request = MagicMock()
        mock_request.url.path = "/docs"

        mock_call_next = AsyncMock()
        mock_response = Response(content="Test response")
        mock_call_next.return_value = mock_response

        # Act
        response = await middleware.dispatch(mock_request, mock_call_next)

        # Assert
        assert response == mock_response
        mock_is_unprotected_path.assert_called_once_with("/docs")
        mock_call_next.assert_called_once_with(mock_request)

    @patch('middlewares.token_middleware.is_unprotected_path')
    @patch('middlewares.token_middleware.check_headers_token')
    @patch('middlewares.token_middleware.extract_token')
    @patch('middlewares.token_middleware.get_token_info')
    @patch('middlewares.token_middleware.check_token')
    @patch('middlewares.token_middleware.generate_state_info')
    @patch('middlewares.token_middleware.store_token_info_in_state')
    async def test_dispatch_protected_path(self, mock_store_token_info_in_state, mock_generate_state_info,
                                          mock_check_token, mock_get_token_info, mock_extract_token,
                                          mock_check_headers_token, mock_is_unprotected_path):
        # Arrange
        mock_is_unprotected_path.return_value = False
        mock_extract_token.return_value = "test-token"
        mock_get_token_info.return_value = {"active": True}
        mock_generate_state_info.return_value = {"user_uuid": "user-123"}

        mock_app = MagicMock()
        middleware = TokenVerificationMiddleware(mock_app)

        mock_request = MagicMock()
        mock_request.url.path = "/protected-path"

        mock_call_next = AsyncMock()
        mock_response = Response(content="Test response")
        mock_call_next.return_value = mock_response

        # Act
        response = await middleware.dispatch(mock_request, mock_call_next)

        # Assert
        assert response == mock_response
        mock_is_unprotected_path.assert_called_once_with("/protected-path")
        mock_check_headers_token.assert_called_once_with(mock_request)
        mock_extract_token.assert_called_once_with(mock_request)
        mock_get_token_info.assert_called_once_with("test-token")
        mock_check_token.assert_called_once_with({"active": True})
        mock_generate_state_info.assert_called_once_with({"active": True})
        mock_store_token_info_in_state.assert_called_once_with({"user_uuid": "user-123"}, mock_request)
        mock_call_next.assert_called_once_with(mock_request)

    @patch('middlewares.token_middleware.is_unprotected_path')
    async def test_dispatch_exception_handling(self, mock_is_unprotected_path):
        # Arrange
        mock_is_unprotected_path.return_value = False

        mock_app = MagicMock()
        middleware = TokenVerificationMiddleware(mock_app)

        mock_request = MagicMock()
        mock_request.url.path = "/protected-path"
        mock_request.headers = {}  # This will cause check_headers_token to raise an exception

        mock_call_next = AsyncMock()

        # Act
        response = await middleware.dispatch(mock_request, mock_call_next)

        # Assert
        assert isinstance(response, JSONResponse)
        assert response.status_code == 401
        assert response.body == b'{"detail":"Token manquant ou invalide"}'
        mock_call_next.assert_not_called()