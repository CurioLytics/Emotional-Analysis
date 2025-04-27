"""
Tests for Supabase connection functionality.

This module contains tests for the Supabase client initialization
and connection functions.
"""

import os
import pytest
from unittest.mock import patch, MagicMock
import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.parent.absolute()
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# Import the function from the journal page
from pages.journal_page import init_supabase


class TestSupabaseConnection:
    """Test cases for Supabase connection functionality."""

    def test_init_supabase_success(self):
        """Test successful Supabase client initialization."""
        # Setup: Mock the Supabase client and response
        mock_execute = MagicMock(return_value=MagicMock(data=[{"id": "test-id"}]))
        mock_limit = MagicMock(return_value=MagicMock(execute=mock_execute))
        mock_select = MagicMock(return_value=MagicMock(limit=mock_limit))
        mock_table = MagicMock(return_value=MagicMock(select=mock_select))
        
        mock_client = MagicMock()
        mock_client.table = mock_table
        
        # Mock the create_client function
        with patch('pages.journal_page.create_client', return_value=mock_client) as mock_create:
            # Mock environment variables
            with patch.dict(os.environ, {
                "SUPABASE_URL": "https://test-url.supabase.co",
                "SUPABASE_KEY": "test-key"
            }):
                # Call the function
                client = init_supabase()
                
                # Assertions
                assert client is mock_client
                mock_create.assert_called_once_with(
                    "https://test-url.supabase.co", 
                    "test-key"
                )
                mock_table.assert_called_once_with("documents")
                mock_select.assert_called_once_with("id")
                mock_limit.assert_called_once_with(1)
                mock_execute.assert_called_once()

    def test_init_supabase_missing_env_vars(self):
        """Test Supabase initialization with missing environment variables."""
        # Setup: Empty environment variables
        with patch.dict(os.environ, {}, clear=True):
            # Mock streamlit functions
            with patch('pages.journal_page.st.error') as mock_error:
                with patch('pages.journal_page.st.stop') as mock_stop:
                    # Call the function - it should raise an exception
                    with pytest.raises(Exception):
                        init_supabase()
                    
                    # Assert streamlit functions were called
                    mock_error.assert_called_once()
                    mock_stop.assert_called_once()

    def test_init_supabase_connection_error(self):
        """Test Supabase initialization with connection error."""
        # Setup: Mock connection error
        with patch('pages.journal_page.create_client') as mock_create:
            mock_create.side_effect = Exception("Connection error")
            
            # Mock streamlit functions
            with patch('pages.journal_page.st.error') as mock_error:
                with patch('pages.journal_page.st.stop') as mock_stop:
                    # Mock environment variables
                    with patch.dict(os.environ, {
                        "SUPABASE_URL": "https://test-url.supabase.co",
                        "SUPABASE_KEY": "test-key"
                    }):
                        # Call the function - it should raise an exception
                        with pytest.raises(Exception):
                            init_supabase()
                        
                        # Assert streamlit functions were called
                        mock_error.assert_called_once()
                        mock_stop.assert_called_once()
```
