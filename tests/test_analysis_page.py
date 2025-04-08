"""
Tests for the journal analysis page functionality.

This module provides test cases for the functions in the analysis-page.py module.
"""

import pytest
import pandas as pd
from datetime import datetime, timedelta
import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.parent.absolute()
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# Import functions to test - fixed the import path to use hyphen instead of underscore
from pages.analysispage import (
    prepare_data_for_line_chart, 
    get_emotion_summary,
    calculate_dominant_emotion,
    EMOTION_COLUMNS
)

# Mock data for testing
@pytest.fixture
def sample_emotion_data():
    """Create sample emotion data for testing."""
    data = {
        'date': [
            datetime.now() - timedelta(days=5),
            datetime.now() - timedelta(days=4),
            datetime.now() - timedelta(days=3),
            datetime.now() - timedelta(days=2),
            datetime.now() - timedelta(days=1)
        ]
    }
    
    # Add emotion columns with random values
    for emotion in EMOTION_COLUMNS:
        if emotion == 'happiness':
            # Make happiness the dominant emotion for testing
            data[emotion] = [75, 80, 85, 70, 75]
        elif emotion == 'sadness':
            # Make this vary a lot for testing variability
            data[emotion] = [15, 5, 25, 10, 20]
        else:
            # Other emotions with lower values
            data[emotion] = [10, 5, 2, 8, 4]
    
    return pd.DataFrame(data)

@pytest.fixture
def empty_emotion_data():
    """Create an empty DataFrame with the expected columns."""
    empty_df = pd.DataFrame(columns=['date'] + EMOTION_COLUMNS)
    return empty_df

def test_prepare_data_for_line_chart(sample_emotion_data):
    """
    Test the prepare_data_for_line_chart function with sample data.
    
    This test verifies that the function correctly converts wide-format emotion data
    to long format suitable for plotting.
    """
    # Act
    result = prepare_data_for_line_chart(sample_emotion_data)
    
    # Assert
    assert 'emotion' in result.columns
    assert 'score' in result.columns
    assert 'date' in result.columns
    
    # Check that we have the right number of rows (original_rows * number_of_emotions)
    assert len(result) == len(sample_emotion_data) * len(EMOTION_COLUMNS)
    
    # Check that all emotions are represented in the transformed data
    assert set(result['emotion'].unique()) == set(EMOTION_COLUMNS)

def test_prepare_data_for_line_chart_empty_data(empty_emotion_data):
    """
    Test the prepare_data_for_line_chart function with empty data.
    
    This test verifies that the function handles empty DataFrames gracefully.
    """
    # Act
    result = prepare_data_for_line_chart(empty_emotion_data)
    
    # Assert
    assert result.empty
    assert list(result.columns) == ['date', 'emotion', 'score']

def test_get_emotion_summary(sample_emotion_data):
    """
    Test the get_emotion_summary function with sample data.
    
    This test verifies that the function correctly calculates average scores
    for each emotion.
    """
    # Act
    result = get_emotion_summary(sample_emotion_data)
    
    # Assert
    assert isinstance(result, dict)
    assert len(result) == len(EMOTION_COLUMNS)
    
    # Check all emotions are included in the summary
    for emotion in EMOTION_COLUMNS:
        assert emotion in result
    
    # Check that happiness is the highest (as per our sample data)
    assert max(result.items(), key=lambda x: x[1])[0] == 'happiness'

def test_get_emotion_summary_empty_data(empty_emotion_data):
    """
    Test the get_emotion_summary function with empty data.
    
    This test verifies that the function handles empty DataFrames gracefully.
    """
    # Act
    result = get_emotion_summary(empty_emotion_data)
    
    # Assert
    assert result == {}

def test_calculate_dominant_emotion(sample_emotion_data):
    """
    Test the calculate_dominant_emotion function with sample data.
    
    This test verifies that the function correctly identifies the dominant emotion
    and its score.
    """
    # Act
    dominant_emotion, score = calculate_dominant_emotion(sample_emotion_data)
    
    # Assert
    assert dominant_emotion == 'happiness'
    assert score > 0
    assert isinstance(score, float)

def test_calculate_dominant_emotion_empty_data(empty_emotion_data):
    """
    Test the calculate_dominant_emotion function with empty data.
    
    This test verifies that the function handles empty DataFrames gracefully.
    """
    # Act
    dominant_emotion, score = calculate_dominant_emotion(empty_emotion_data)
    
    # Assert
    assert dominant_emotion == ""
    assert score == 0.0