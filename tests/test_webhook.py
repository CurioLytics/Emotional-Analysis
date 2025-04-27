"""
Tests for the webhook utility functions.

This module contains tests for the webhook utility functions used for
communicating with n8n webhooks.
"""

import os
import json
import pytest
from unittest.mock import patch, MagicMock
import sys

# Add parent directory to path to allow imports from utils
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.webhook import send_message_to_llm, get_webhook_credentials, DEFAULT_WEBHOOK_URL, DEFAULT_BEARER_TOKEN


class TestWebhookFunctions:
    """Test cases for webhook communication functions."""

    def test_get_webhook_credentials_with_env_vars(self):
        """Test getting webhook credentials when environment variables are set."""
        # Setup: Set environment variables
        with patch.dict(os.environ, {
            "N8N_WEBHOOK_URL": "https://test-webhook-url.com",
            "N8N_BEARER_TOKEN": "test-token-123"
        }):
            # Execute
            webhook_url, bearer_token = get_webhook_credentials()
            
            # Assert
            assert webhook_url == "https://test-webhook-url.com"
            assert bearer_token == "test-token-123"

    def test_get_webhook_credentials_without_env_vars(self):
        """Test getting webhook credentials when environment variables are not set (using defaults)."""
        # Setup: Ensure environment variables are not set but respect the default parameter
        with patch('os.getenv') as mock_getenv:
            # Make os.getenv return the second argument (default) when called
            mock_getenv.side_effect = lambda key, default=None: default
            
            # Execute
            webhook_url, bearer_token = get_webhook_credentials()
            
            # Assert: Should use default values
            assert webhook_url == DEFAULT_WEBHOOK_URL
            assert bearer_token == DEFAULT_BEARER_TOKEN

    @patch('utils.webhook.requests.post')
    def test_send_message_to_llm_success(self, mock_post):
        """Test sending a message to LLM with successful response."""
        # Setup: Mock successful response
        mock_response = MagicMock()
        mock_response.json.return_value = {"output": "Test response from LLM"}
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response
        
        # Execute
        success, response = send_message_to_llm("test-session-id", "Test message")
        
        # Assert
        assert success is True
        assert response == "Test response from LLM"
        mock_post.assert_called_once()

    @patch('utils.webhook.requests.post')
    def test_send_message_to_llm_http_error(self, mock_post):
        """Test sending a message to LLM with HTTP error."""
        # Setup: Mock HTTP error
        import requests
        mock_post.side_effect = requests.exceptions.HTTPError("404 Client Error")
        
        # Execute
        success, response = send_message_to_llm("test-session-id", "Test message")
        
        # Assert
        assert success is False
        assert "Webhook request failed" in response
        assert "404 Client Error" in response

    @patch('utils.webhook.requests.post')
    def test_send_message_to_llm_json_decode_error(self, mock_post):
        """Test sending a message to LLM with JSON decode error."""
        # Setup: Mock invalid JSON response
        mock_response = MagicMock()
        mock_response.json.side_effect = json.JSONDecodeError("Invalid JSON", "{", 0)
        mock_response.text = "Not a JSON response"
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response
        
        # Execute
        success, response = send_message_to_llm("test-session-id", "Test message")
        
        # Assert
        assert success is False
        assert "Failed to parse webhook response" in response

    @patch('utils.webhook.requests.post')
    def test_send_message_to_llm_unexpected_error(self, mock_post):
        """Test sending a message to LLM with unexpected error."""
        # Setup: Mock unexpected error
        mock_post.side_effect = Exception("Unexpected error")
        
        # Execute
        success, response = send_message_to_llm("test-session-id", "Test message")
        
        # Assert
        assert success is False
        assert "Unexpected error" in response