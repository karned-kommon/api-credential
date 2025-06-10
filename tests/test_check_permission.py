import tests.env_setup
import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from fastapi import HTTPException, Request
from decorators.check_permission import check_roles, check_permissions


class TestCheckPermission:
    def test_check_roles_success(self):
        # Arrange
        list_roles = ["admin", "user", "editor"]
        permissions = ["user"]
        
        # Act
        # Should not raise an exception
        check_roles(list_roles, permissions)
    
    def test_check_roles_multiple_permissions_success(self):
        # Arrange
        list_roles = ["admin", "user", "editor"]
        permissions = ["manager", "editor"]
        
        # Act
        # Should not raise an exception
        check_roles(list_roles, permissions)
    
    def test_check_roles_failure(self):
        # Arrange
        list_roles = ["user", "editor"]
        permissions = ["admin"]
        
        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            check_roles(list_roles, permissions)
        
        assert exc_info.value.status_code == 403
        assert "Insufficient permissions" in exc_info.value.detail
        assert "Need : admin" in exc_info.value.detail
        assert "Got : user, editor" in exc_info.value.detail
    
    @pytest.mark.asyncio
    async def test_check_permissions_decorator_success(self):
        # Arrange
        mock_request = MagicMock(spec=Request)
        mock_request.state.token_info = {"license_roles": ["admin", "user"]}
        
        # Create a decorated function
        @check_permissions(["user"])
        async def test_function(request):
            return "success"
        
        # Act
        with patch('decorators.check_permission.logging') as mock_logging:
            result = await test_function(mock_request)
        
        # Assert
        assert result == "success"
        mock_logging.info.assert_any_call("Checking permissions ['user']")
        mock_logging.info.assert_any_call(f"License: {mock_request}")
    
    @pytest.mark.asyncio
    async def test_check_permissions_decorator_failure(self):
        # Arrange
        mock_request = MagicMock(spec=Request)
        mock_request.state.token_info = {"license_roles": ["editor"]}
        
        # Create a decorated function
        @check_permissions(["admin"])
        async def test_function(request):
            return "success"
        
        # Act & Assert
        with patch('decorators.check_permission.logging') as mock_logging:
            with pytest.raises(HTTPException) as exc_info:
                await test_function(mock_request)
        
        assert exc_info.value.status_code == 403
        assert "Insufficient permissions" in exc_info.value.detail
        mock_logging.info.assert_any_call("Checking permissions ['admin']")
        mock_logging.info.assert_any_call(f"License: {mock_request}")