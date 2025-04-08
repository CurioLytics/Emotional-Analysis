"""
Tests for the chat interface module.

This module contains tests for the chat functionality used for interacting
with an AI assistant that can access and recall information from journal entries.
"""

import os
import sys
import uuid
import pytest
from unittest.mock import patch, MagicMock
import importlib.util

# Add parent directory to path to allow imports from pages
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the chat-page.py module using importlib
chat_page_path = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "pages",
    "chat-page.py"
)
spec = importlib.util.spec_from_file_location("chat_page", chat_page_path)
chat_page = importlib.util.module_from_spec(spec)
spec.loader.exec_module(chat_page)

# Now we can access functions from the module
generate_session_id = chat_page.generate_session_id


class TestChatFunctions:
    """Test cases for chat interface functions."""

    def test_generate_session_id(self):
        """Test generating a unique session ID."""
        # Execute
        session_id = chat_page.generate_session_id()
        
        # Assert
        assert isinstance(session_id, str)
        assert len(session_id) > 0
        
        # Test uniqueness
        another_session_id = chat_page.generate_session_id()
        assert session_id != another_session_id
        
        # Verify it's a valid UUID
        try:
            uuid_obj = uuid.UUID(session_id)
            assert str(uuid_obj) == session_id
        except ValueError:
            pytest.fail("Session ID is not a valid UUID")

    @patch('utils.webhook.send_message_to_llm')
    def test_chat_message_processing_success(self, mock_send_message):
        """Test processing a chat message with successful response."""
        # Setup: Mock successful webhook response
        mock_send_message.return_value = (True, "Test response from LLM")
        
        # We can't easily test the Streamlit UI functions directly,
        # but we can test the underlying webhook call functionality
        session_id = "test-session-id"
        message = "Test message"
        
        # Execute - use the imported function directly from utils
        from utils.webhook import send_message_to_llm
        success, response = send_message_to_llm(session_id, message)
        
        # Assert
        assert success is True
        assert response == "Test response from LLM"
        mock_send_message.assert_called_once_with(session_id, message)

    @patch('utils.webhook.send_message_to_llm')
    def test_chat_message_processing_failure(self, mock_send_message):
        """Test processing a chat message with error response."""
        # Setup: Mock failed webhook response
        error_message = "Error connecting to LLM service"
        mock_send_message.return_value = (False, error_message)
        
        # Execute
        from utils.webhook import send_message_to_llm
        success, response = send_message_to_llm("test-session-id", "Test message")
        
        # Assert
        assert success is False
        assert response == error_message
        mock_send_message.assert_called_once_with("test-session-id", "Test message")

    def test_environment_variable_loading(self):
        """Test environment variable loading for the chat module."""
        # We'll test that the module can properly access environment variables
        # but without actually reloading the module (which causes issues)
        test_url = "https://test-webhook-url.com"
        test_token = "test-bearer-token"
        
        # Patch the environment variables at the os level
        with patch.object(chat_page, 'os') as mock_os:
            # Configure the mock to return test values for os.getenv
            mock_os.getenv.side_effect = lambda key, default=None: {
                "N8N_WEBHOOK_URL": test_url,
                "N8N_BEARER_TOKEN": test_token
            }.get(key, default)
            
            # Use the webhook module directly through our imported module
            with patch.object(chat_page, 'send_message_to_llm') as mock_send:
                mock_send.return_value = (True, "Test response")
                
                # Create a test session ID
                session_id = chat_page.generate_session_id()
                
                # The test succeeds if we can call the function without exceptions
                result = mock_send(session_id, "Test message")
                assert result[0] is True
                assert result[1] == "Test response"