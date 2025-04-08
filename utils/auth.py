"""
Authentication utilities for the Journal and Chat Application.

This module provides standardized functions for handling authentication
and environment variables related to authentication.
"""

import os
import logging
from typing import Optional, Tuple
from dotenv import load_dotenv
from supabase import create_client, Client

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

def get_env(key: str, default: Optional[str] = None) -> str:
    """
    Get an environment variable with optional default value.
    
    Args:
        key: The name of the environment variable
        default: Optional default value if variable is not set
        
    Returns:
        str: The value of the environment variable
        
    Raises:
        ValueError: If the variable is not set and no default is provided
    """
    value = os.environ.get(key, default)
    if value is None:
        raise ValueError(f"Environment variable {key} is not set and no default provided")
    return value

def get_supabase_credentials() -> Tuple[str, str]:
    """
    Get Supabase credentials from environment variables.
    
    Returns:
        Tuple[str, str]: Supabase URL and key
        
    Raises:
        ValueError: If Supabase credentials are not found in environment variables
    """
    url = get_env("SUPABASE_URL")
    key = get_env("SUPABASE_KEY")
    
    if not url or not key:
        error_msg = "Supabase credentials not found in environment variables"
        logger.error(error_msg)
        raise ValueError(error_msg)
    
    return url, key

def get_supabase_client() -> Client:
    """
    Initialize and return a Supabase client with credentials from environment variables.
    
    Returns:
        Client: Initialized Supabase client
        
    Raises:
        ValueError: If Supabase credentials are missing or invalid
        ConnectionError: If Supabase connection fails
    """
    url, key = get_supabase_credentials()
    
    try:
        client = create_client(url, key)
        # Test the connection with a simple query
        test_response = client.table("documents").select("id").limit(1).execute()
        logger.info("Supabase connection successful")
        return client
    except Exception as e:
        error_msg = f"Failed to connect to Supabase: {str(e)}"
        logger.error(error_msg)
        raise ConnectionError(error_msg)

def get_webhook_credentials() -> Tuple[str, str, str]:
    """
    Get webhook credentials from environment variables.
    
    Returns:
        Tuple[str, str, str]: Webhook chat URL, update URL, and bearer token
    """
    chat_url = get_env("N8N_WEBHOOK_CHAT_URL", "https://curiolytics.app.n8n.cloud/webhook/webhook-path")
    # Updated the default URL for the webhook update endpoint
    update_url = get_env("N8N_WEBHOOK_UPDATE_URL", "https://curiolytics.app.n8n.cloud/webhook/webhook-update-supabase")
    bearer_token = get_env("N8N_BEARER_TOKEN", "")
    
    return chat_url, update_url, bearer_token