import pytest
from datetime import datetime
from content.generator.base_generator import BaseContentGenerator

class TestContentGenerator(BaseContentGenerator):
    """
    Test implementation of BaseContentGenerator for testing purposes.
    """
    
    def generate_content(self, prompt: str, context: dict = None) -> str:
        """Generate test content."""
        return f"Test content for prompt: {prompt}"
    
    def validate_content(self, content: str) -> bool:
        """Validate test content."""
        return len(content) > 0

@pytest.fixture
def generator_config() -> dict:
    """
    Create test generator configuration.
    
    Returns:
        dict: Generator configuration
    """
    return {
        "model_name": "gpt-4",
        "temperature": 0.7,
        "max_tokens": 2000
    }

@pytest.fixture
def sample_prompt() -> str:
    """
    Create sample prompt for testing.
    
    Returns:
        str: Sample prompt
    """
    return "Generate market analysis for BTC/USDT"

@pytest.fixture
def sample_context() -> dict:
    """
    Create sample context for testing.
    
    Returns:
        dict: Sample context
    """
    return {
        "timeframe": "1h",
        "market_trend": "bullish",
        "key_levels": {
            "support": 49000,
            "resistance": 51000
        }
    }

def test_generator_initialization(generator_config):
    """
    Test generator initialization.
    
    Args:
        generator_config (dict): Generator configuration
    """
    generator = TestContentGenerator(generator_config)
    assert generator.config == generator_config
    assert generator.model is not None

def test_generate_content(generator_config, sample_prompt, sample_context):
    """
    Test content generation.
    
    Args:
        generator_config (dict): Generator configuration
        sample_prompt (str): Sample prompt
        sample_context (dict): Sample context
    """
    generator = TestContentGenerator(generator_config)
    content = generator.generate_content(sample_prompt, sample_context)
    
    assert isinstance(content, str)
    assert len(content) > 0
    assert sample_prompt in content

def test_validate_content(generator_config):
    """
    Test content validation.
    
    Args:
        generator_config (dict): Generator configuration
    """
    generator = TestContentGenerator(generator_config)
    content = "Test content"
    
    assert generator.validate_content(content) is True
    assert generator.validate_content("") is False

def test_format_prompt(generator_config, sample_prompt, sample_context):
    """
    Test prompt formatting.
    
    Args:
        generator_config (dict): Generator configuration
        sample_prompt (str): Sample prompt
        sample_context (dict): Sample context
    """
    generator = TestContentGenerator(generator_config)
    formatted_prompt = generator.format_prompt(sample_prompt, sample_context)
    
    assert isinstance(formatted_prompt, str)
    assert sample_prompt in formatted_prompt
    assert "Context:" in formatted_prompt
    assert "timeframe" in formatted_prompt
    assert "market_trend" in formatted_prompt

def test_get_system_message(generator_config):
    """
    Test system message generation.
    
    Args:
        generator_config (dict): Generator configuration
    """
    generator = TestContentGenerator(generator_config)
    system_message = generator.get_system_message()
    
    assert isinstance(system_message, str)
    assert "expert" in system_message.lower()
    assert "financial" in system_message.lower()
    assert "market analysis" in system_message.lower()

def test_generate_with_retry(generator_config, sample_prompt, sample_context):
    """
    Test content generation with retry logic.
    
    Args:
        generator_config (dict): Generator configuration
        sample_prompt (str): Sample prompt
        sample_context (dict): Sample context
    """
    generator = TestContentGenerator(generator_config)
    content = generator.generate_with_retry(sample_prompt, sample_context)
    
    assert isinstance(content, str)
    assert len(content) > 0
    assert sample_prompt in content

def test_metrics(generator_config):
    """
    Test generator metrics.
    
    Args:
        generator_config (dict): Generator configuration
    """
    generator = TestContentGenerator(generator_config)
    metrics = generator.get_metrics()
    
    assert isinstance(metrics, dict)
    assert "total_generations" in metrics
    assert "successful_generations" in metrics
    assert "failed_generations" in metrics
    assert "average_length" in metrics
    assert "average_generation_time" in metrics

def test_error_handling(generator_config, sample_prompt):
    """
    Test error handling in content generation.
    
    Args:
        generator_config (dict): Generator configuration
        sample_prompt (str): Sample prompt
    """
    generator = TestContentGenerator(generator_config)
    
    # Test with invalid prompt
    with pytest.raises(Exception):
        generator.generate_with_retry("", max_retries=1)
    
    # Test with invalid context
    with pytest.raises(Exception):
        generator.generate_with_retry(sample_prompt, context="invalid", max_retries=1) 