import pytest
import logging
import sys
from unittest.mock import patch, MagicMock
from ...core.logger import (
    get_logger,
    setup_logging,
    get_trading_logger,
    get_api_logger,
    get_data_logger,
    get_content_logger,
    get_system_logger
)

@pytest.fixture
def mock_settings():
    """Create mock settings for testing."""
    with patch('...core.logger.settings') as mock:
        mock.LOG_LEVEL = "DEBUG"
        mock.LOG_FORMAT = "%(name)s - %(levelname)s - %(message)s"
        yield mock

def test_get_logger(mock_settings):
    """Test getting a logger instance."""
    # Test with default level
    logger = get_logger("test")
    assert isinstance(logger, logging.Logger)
    assert logger.name == "test"
    assert logger.level == logging.DEBUG
    assert len(logger.handlers) == 1
    assert isinstance(logger.handlers[0], logging.StreamHandler)
    assert logger.handlers[0].stream == sys.stdout
    
    # Test with custom level
    logger = get_logger("test", level="INFO")
    assert logger.level == logging.INFO
    
    # Test that handlers are not duplicated
    logger = get_logger("test")
    assert len(logger.handlers) == 1

def test_setup_logging(mock_settings):
    """Test setting up root logger."""
    setup_logging()
    
    root_logger = logging.getLogger()
    assert root_logger.level == logging.DEBUG
    assert len(root_logger.handlers) == 1
    assert isinstance(root_logger.handlers[0], logging.StreamHandler)
    assert root_logger.handlers[0].stream == sys.stdout

def test_get_trading_logger(mock_settings):
    """Test getting trading logger."""
    logger = get_trading_logger()
    assert isinstance(logger, logging.Logger)
    assert logger.name == "trading"
    assert logger.level == logging.DEBUG

def test_get_api_logger(mock_settings):
    """Test getting API logger."""
    logger = get_api_logger()
    assert isinstance(logger, logging.Logger)
    assert logger.name == "api"
    assert logger.level == logging.DEBUG

def test_get_data_logger(mock_settings):
    """Test getting data logger."""
    logger = get_data_logger()
    assert isinstance(logger, logging.Logger)
    assert logger.name == "data"
    assert logger.level == logging.DEBUG

def test_get_content_logger(mock_settings):
    """Test getting content logger."""
    logger = get_content_logger()
    assert isinstance(logger, logging.Logger)
    assert logger.name == "content"
    assert logger.level == logging.DEBUG

def test_get_system_logger(mock_settings):
    """Test getting system logger."""
    logger = get_system_logger()
    assert isinstance(logger, logging.Logger)
    assert logger.name == "system"
    assert logger.level == logging.DEBUG

def test_logger_propagation(mock_settings):
    """Test logger propagation settings."""
    logger = get_logger("test")
    assert not logger.propagate

def test_logger_formatter(mock_settings):
    """Test logger formatter."""
    logger = get_logger("test")
    handler = logger.handlers[0]
    formatter = handler.formatter
    
    # Test format string
    assert "%(name)s" in formatter._fmt
    assert "%(levelname)s" in formatter._fmt
    assert "%(message)s" in formatter._fmt

def test_logger_output(mock_settings, capsys):
    """Test logger output."""
    logger = get_logger("test")
    
    # Test different log levels
    logger.debug("Debug message")
    logger.info("Info message")
    logger.warning("Warning message")
    logger.error("Error message")
    
    # Capture output
    captured = capsys.readouterr()
    
    # Verify output format
    assert "test - DEBUG - Debug message" in captured.out
    assert "test - INFO - Info message" in captured.out
    assert "test - WARNING - Warning message" in captured.out
    assert "test - ERROR - Error message" in captured.out

def test_logger_levels(mock_settings):
    """Test logger level filtering."""
    logger = get_logger("test", level="INFO")
    
    # Test that debug messages are filtered
    logger.debug("Debug message")
    assert not logger.isEnabledFor(logging.DEBUG)
    
    # Test that info messages are not filtered
    logger.info("Info message")
    assert logger.isEnabledFor(logging.INFO)

def test_logger_handlers(mock_settings):
    """Test logger handlers."""
    logger = get_logger("test")
    
    # Test handler type
    assert all(isinstance(h, logging.StreamHandler) for h in logger.handlers)
    
    # Test handler level
    assert all(h.level == logging.DEBUG for h in logger.handlers)
    
    # Test handler stream
    assert all(h.stream == sys.stdout for h in logger.handlers)

def test_logger_cleanup(mock_settings):
    """Test logger cleanup."""
    # Create a logger
    logger = get_logger("test")
    
    # Remove all handlers
    logger.handlers = []
    
    # Get logger again
    logger = get_logger("test")
    
    # Verify handlers are recreated
    assert len(logger.handlers) == 1
    assert isinstance(logger.handlers[0], logging.StreamHandler) 