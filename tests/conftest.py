import pytest
from unittest.mock import patch, MagicMock

@pytest.fixture(autouse=True)
def mock_redis():
    """Mock Redis connection."""
    mock_redis_instance = MagicMock()
    mock_redis_instance.get.return_value = None
    mock_redis_instance.set.return_value = True
    mock_redis_instance.delete.return_value = True

    with patch('redis.Redis', return_value=mock_redis_instance), \
         patch('services.inmemory_service.get_redis_api_db', return_value=mock_redis_instance), \
         patch('middlewares.licence_middleware.r', mock_redis_instance), \
         patch('middlewares.token_middleware.r', mock_redis_instance):
        yield mock_redis_instance
