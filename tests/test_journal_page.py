"""
Tests for the journal entry module.

This module contains tests for the journal entry functions used for
creating, viewing, and managing journal entries.
"""

import os
import pytest
import pandas as pd
from datetime import datetime
from unittest.mock import patch, MagicMock
import sys
import importlib.util
import requests

# Add parent directory to path to allow imports from pages
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the journal-page.py module using importlib
journal_page_path = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "pages",
    "journal-page.py"
)
spec = importlib.util.spec_from_file_location("journal_page", journal_page_path)
journal_page = importlib.util.module_from_spec(spec)
spec.loader.exec_module(journal_page)

# Now we can access functions from the module
init_supabase = journal_page.init_supabase
get_journal_entries = journal_page.get_journal_entries
add_journal_entry = journal_page.add_journal_entry


class TestJournalFunctions:
    """Test cases for journal entry functions."""

    def test_init_supabase_with_valid_credentials(self):
        """Test initializing Supabase client with valid credentials."""
        # Setup: Create a mock that we'll use for patching
        mock_client = MagicMock()
        
        # Use monkeypatch for the journal_page module directly
        with patch.object(journal_page, 'create_client', return_value=mock_client) as mock_create_client:
            with patch.object(journal_page, 'os') as mock_os:
                # Configure the mock to return test values for os.getenv
                mock_os.getenv.side_effect = lambda key, default=None: {
                    "SUPABASE_URL": "https://test-supabase-url.com",
                    "SUPABASE_KEY": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJyb2xlIjoidGVzdCJ9.signature"
                }.get(key, default)
                
                # Execute
                client = init_supabase()
                
                # Assert
                assert client is mock_client
                mock_create_client.assert_called_once_with(
                    "https://test-supabase-url.com", 
                    "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJyb2xlIjoidGVzdCJ9.signature"
                )

    def test_init_supabase_with_missing_credentials(self):
        """Test initializing Supabase client with missing credentials."""
        # Setup: Mock missing environment variables
        with patch.dict(os.environ, {
            "SUPABASE_URL": "",
            "SUPABASE_KEY": ""
        }, clear=True):
            # Execute and Assert
            with patch('streamlit.error') as mock_error:
                with patch('streamlit.stop') as mock_stop:
                    with pytest.raises(Exception):
                        init_supabase()
                    
                    mock_error.assert_called_once()

    def test_get_journal_entries_with_data(self):
        """Test fetching journal entries when data exists."""
        # Setup: Mock Supabase client and response
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.data = [
            {"date-entry": "2025-04-01", "content": "Test journal entry 1"},
            {"date-entry": "2025-04-02", "content": "Test journal entry 2"}
        ]
        
        mock_execute = MagicMock(return_value=mock_response)
        mock_order = MagicMock(return_value=MagicMock(execute=mock_execute))
        mock_select = MagicMock(return_value=MagicMock(order=mock_order))
        mock_table = MagicMock(return_value=MagicMock(select=mock_select))
        
        mock_client.table = mock_table
        
        with patch.object(journal_page, 'init_supabase', return_value=mock_client):
            # Execute
            result = get_journal_entries()
            
            # Assert
            assert isinstance(result, pd.DataFrame)
            assert len(result) == 2
            assert "date" in result.columns
            assert "text" in result.columns

    def test_get_journal_entries_empty(self):
        """Test fetching journal entries when no data exists."""
        # Setup: Mock Supabase client with empty response
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.data = []
        
        mock_execute = MagicMock(return_value=mock_response)
        mock_order = MagicMock(return_value=MagicMock(execute=mock_execute))
        mock_select = MagicMock(return_value=MagicMock(order=mock_order))
        mock_table = MagicMock(return_value=MagicMock(select=mock_select))
        
        mock_client.table = mock_table
        
        with patch.object(journal_page, 'init_supabase', return_value=mock_client):
            # Execute
            result = get_journal_entries()
            
            # Assert
            assert isinstance(result, pd.DataFrame)
            assert len(result) == 0
            assert list(result.columns) == ["date", "text"]

    def test_add_journal_entry_success(self):
        """Test adding a journal entry successfully."""
        # Setup: Mock Supabase client and successful response
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.data = [{"id": "test-id"}]  # Non-empty data indicates success
        
        mock_execute = MagicMock(return_value=mock_response)
        mock_insert = MagicMock(return_value=MagicMock(execute=mock_execute))
        mock_table = MagicMock(return_value=MagicMock(insert=mock_insert))
        
        mock_client.table = mock_table
        
        with patch.object(journal_page, 'init_supabase', return_value=mock_client):
            # Test date and text
            test_date = datetime(2025, 4, 1)
            test_text = "Test journal entry"
            
            # Execute
            result = add_journal_entry(test_date, test_text)
            
            # Assert
            assert result is True
            mock_insert.assert_called_once_with({
                "date-entry": test_date.isoformat(),
                "content": test_text
            })

    def test_add_journal_entry_failure(self):
        """Test adding a journal entry with failure."""
        # Setup: Mock Supabase client and failed response (empty data)
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.data = []  # Empty data indicates failure
        
        mock_execute = MagicMock(return_value=mock_response)
        mock_insert = MagicMock(return_value=MagicMock(execute=mock_execute))
        mock_table = MagicMock(return_value=MagicMock(insert=mock_insert))
        
        mock_client.table = mock_table
        
        with patch.object(journal_page, 'init_supabase', return_value=mock_client):
            # Test date and text
            test_date = datetime(2025, 4, 1)
            test_text = "Test journal entry"
            
            # Execute
            result = add_journal_entry(test_date, test_text)
            
            # Assert
            assert result is False

    @patch('requests.post')
    def test_send_webhook_notification_success(self, mock_post):
        """Test sending webhook notification after journal entry changes with successful response."""
        # Setup: Mock successful response
        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response
        
        test_id = "test-entry-id"
        test_content = "Test journal content"
        
        # Execute
        with patch.object(journal_page, 'get_webhook_token', return_value="test-token"):
            success, msg = journal_page.send_webhook_notification(test_id, test_content)
        
        # Assert
        assert success is True
        assert "successfully" in msg
        mock_post.assert_called_once_with(
            journal_page.WEBHOOK_UPDATE_URL,
            json={"id": test_id, "text": test_content},
            headers={
                "Authorization": "Bearer test-token",
                "Content-Type": "application/json"
            }
        )

    @patch('requests.post')
    def test_send_webhook_notification_request_error(self, mock_post):
        """Test sending webhook notification with request error."""
        # Setup: Mock HTTP error
        mock_post.side_effect = requests.exceptions.RequestException("Connection error")
        
        test_id = "test-entry-id"
        test_content = "Test journal content"
        
        # Execute
        with patch.object(journal_page, 'get_webhook_token', return_value="test-token"):
            success, msg = journal_page.send_webhook_notification(test_id, test_content)
        
        # Assert
        assert success is False
        assert "failed" in msg
        assert "Connection error" in msg

    @patch('requests.post')
    def test_send_webhook_notification_unexpected_error(self, mock_post):
        """Test sending webhook notification with unexpected error."""
        # Setup: Mock unexpected error
        mock_post.side_effect = Exception("Unexpected error")
        
        test_id = "test-entry-id"
        test_content = "Test journal content"
        
        # Execute
        with patch.object(journal_page, 'get_webhook_token', return_value="test-token"):
            success, msg = journal_page.send_webhook_notification(test_id, test_content)
        
        # Assert
        assert success is False
        assert "Unexpected error" in msg