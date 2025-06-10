import tests.env_setup
import pytest
import asyncio
from unittest.mock import patch, MagicMock
from decorators.log_time import log_time, log_time_async


class TestLogTime:
    @patch('decorators.log_time.logging')
    @patch('decorators.log_time.time')
    @patch('decorators.log_time.random')
    def test_log_time_decorator(self, mock_random, mock_time, mock_logging):
        # Arrange
        mock_random.randint.return_value = 12345
        mock_time.time.side_effect = [100.0, 105.0]  # Start time, end time
        
        # Create a test function
        @log_time
        def test_function(a, b):
            return a + b
        
        # Act
        result = test_function(3, 4)
        
        # Assert
        assert result == 7
        mock_random.randint.assert_called_once_with(1, 1000000)
        assert mock_time.time.call_count == 2
        mock_logging.info.assert_any_call("test_function: Start 12345", 12345)
        mock_logging.info.assert_any_call("test_function: End 12345 | Execution time: 5.0000 seconds")
    
    @pytest.mark.asyncio
    @patch('decorators.log_time.logging')
    @patch('decorators.log_time.time')
    @patch('decorators.log_time.random')
    async def test_log_time_async_decorator(self, mock_random, mock_time, mock_logging):
        # Arrange
        mock_random.randint.return_value = 67890
        mock_time.time.side_effect = [200.0, 203.0]  # Start time, end time
        
        # Create a test async function
        @log_time_async
        async def test_async_function(a, b):
            await asyncio.sleep(0.01)  # Small delay
            return a * b
        
        # Act
        result = await test_async_function(5, 6)
        
        # Assert
        assert result == 30
        mock_random.randint.assert_called_once_with(1, 1000000)
        assert mock_time.time.call_count == 2
        mock_logging.info.assert_any_call("test_async_function: Start 67890")
        mock_logging.info.assert_any_call("test_async_function: End 67890 | Execution time: 3.0000 seconds")