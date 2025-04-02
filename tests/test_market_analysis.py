import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from content.generators.market_analysis import MarketAnalysisGenerator

@pytest.fixture
def generator_config():
    return {
        'model_name': 'gpt-4',
        'temperature': 0.7,
        'max_tokens': 1000,
        'rsi_period': 14,
        'ma_periods': [20, 50, 200]
    }

@pytest.fixture
def sample_market_data():
    # Generate sample market data with a clear trend
    dates = pd.date_range(start='2024-01-01', periods=100, freq='1H')
    trend = np.linspace(50000, 55000, 100)
    noise = np.random.normal(0, 100, 100)
    
    data = pd.DataFrame({
        'open': trend + noise,
        'high': trend + noise + abs(np.random.normal(0, 100, 100)),
        'low': trend + noise - abs(np.random.normal(0, 100, 100)),
        'close': trend + noise,
        'volume': np.random.normal(100, 20, 100)
    }, index=dates)
    
    # Ensure OHLCV relationships are valid
    data['high'] = data[['open', 'close']].max(axis=1) + abs(np.random.normal(0, 100, 100))
    data['low'] = data[['open', 'close']].min(axis=1) - abs(np.random.normal(0, 100, 100))
    data['volume'] = abs(data['volume'])
    
    return data

def test_generator_initialization(generator_config):
    """Test generator initialization with config"""
    generator = MarketAnalysisGenerator(generator_config)
    
    assert generator.rsi_period == generator_config['rsi_period']
    assert generator.ma_periods == generator_config['ma_periods']

def test_analyze_market_data(generator_config, sample_market_data):
    """Test market data analysis"""
    generator = MarketAnalysisGenerator(generator_config)
    analysis = generator._analyze_market_data(sample_market_data)
    
    # Check required fields
    required_fields = [
        'current_price', 'rsi', 'macd', 'trend', 'key_levels',
        'moving_averages', 'bollinger_bands', 'price_change_24h',
        'volume_change_24h'
    ]
    assert all(field in analysis for field in required_fields)
    
    # Check data types and ranges
    assert isinstance(analysis['current_price'], float)
    assert 0 <= analysis['rsi'] <= 100
    assert isinstance(analysis['trend'], str)
    assert isinstance(analysis['key_levels'], dict)
    assert 'support' in analysis['key_levels']
    assert 'resistance' in analysis['key_levels']
    assert len(analysis['moving_averages']) == len(generator_config['ma_periods'])

def test_determine_trend(generator_config, sample_market_data):
    """Test trend determination"""
    generator = MarketAnalysisGenerator(generator_config)
    trend = generator._determine_trend(sample_market_data)
    
    assert isinstance(trend, str)
    assert trend in ['strong_uptrend', 'uptrend', 'weak_uptrend', 'downtrend']

def test_identify_key_levels(generator_config, sample_market_data):
    """Test key level identification"""
    generator = MarketAnalysisGenerator(generator_config)
    key_levels = generator._identify_key_levels(sample_market_data)
    
    assert isinstance(key_levels, dict)
    assert 'support' in key_levels
    assert 'resistance' in key_levels
    assert len(key_levels['support']) == 2  # recent lows and bb lower
    assert len(key_levels['resistance']) == 2  # recent highs and bb upper
    
    # Check support levels are below resistance levels
    assert max(key_levels['support']) < min(key_levels['resistance'])

def test_calculate_price_change(generator_config, sample_market_data):
    """Test price change calculation"""
    generator = MarketAnalysisGenerator(generator_config)
    price_change = generator._calculate_price_change(sample_market_data)
    
    assert isinstance(price_change, float)
    # With our sample data (uptrend), price change should be positive
    assert price_change > 0

def test_calculate_volume_change(generator_config, sample_market_data):
    """Test volume change calculation"""
    generator = MarketAnalysisGenerator(generator_config)
    volume_change = generator._calculate_volume_change(sample_market_data)
    
    assert isinstance(volume_change, float)

def test_format_prompt(generator_config, sample_market_data):
    """Test prompt formatting"""
    generator = MarketAnalysisGenerator(generator_config)
    analysis = generator._analyze_market_data(sample_market_data)
    prompt = generator._format_prompt(analysis)
    
    assert isinstance(prompt, str)
    assert 'Current Price' in prompt
    assert 'Technical Indicators' in prompt
    assert 'Market Structure' in prompt
    
    # Test with additional context
    context = {'additional_info': 'Test context'}
    prompt_with_context = generator._format_prompt(analysis, context)
    assert 'Test context' in prompt_with_context

def test_generate_content(generator_config, sample_market_data):
    """Test content generation"""
    generator = MarketAnalysisGenerator(generator_config)
    content = generator.generate_content(sample_market_data)
    
    assert isinstance(content, str)
    assert len(content) > 0
    
    # Test with additional context
    context = {'additional_info': 'Test context'}
    content_with_context = generator.generate_content(sample_market_data, context)
    assert isinstance(content_with_context, str)
    assert len(content_with_context) > 0

def test_error_handling(generator_config):
    """Test error handling with invalid data"""
    generator = MarketAnalysisGenerator(generator_config)
    
    # Test with empty DataFrame
    empty_data = pd.DataFrame()
    with pytest.raises(Exception):
        generator.generate_content(empty_data)
    
    # Test with missing columns
    invalid_data = pd.DataFrame({'close': [1, 2, 3]})
    with pytest.raises(Exception):
        generator.generate_content(invalid_data)
    
    # Test with invalid values
    invalid_data = pd.DataFrame({
        'open': [np.nan],
        'high': [np.nan],
        'low': [np.nan],
        'close': [np.nan],
        'volume': [np.nan]
    })
    with pytest.raises(Exception):
        generator.generate_content(invalid_data) 