"""
Utility module for n8n webhook communication.

This module provides functions for communicating with n8n webhooks,
including sending messages to LLMs and handling responses.
"""

import requests
import json
import logging
from typing import Dict, Any, Optional, Tuple

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import authentication functions
from utils.auth import get_env, get_webhook_credentials

def send_message_to_llm(session_id: str, message: str) -> Tuple[bool, str]:
    """
    Send a message to LLM via n8n webhook.
    
    Args:
        session_id (str): Unique session identifier
        message (str): User message to send to LLM
    
    Returns:
        Tuple[bool, str]: Success status and response message or error
    """
    chat_url, _, bearer_token = get_webhook_credentials()
    
    headers = {
        "Authorization": f"Bearer {bearer_token}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "sessionId": session_id,
        "chatInput": message
    }
    
    try:
        logger.info(f"Sending message to webhook for session {session_id}")
        response = requests.post(chat_url, json=payload, headers=headers)
        response.raise_for_status()  # Raise exception for 4XX/5XX status codes
        
        response_data = response.json()
        return True, response_data.get("output", "No output received from LLM")
    
    except requests.exceptions.RequestException as e:
        error_msg = f"Webhook request failed: {str(e)}"
        logger.error(error_msg)
        return False, error_msg
    
    except json.JSONDecodeError as e:
        error_msg = f"Failed to parse webhook response: {response.text}"
        logger.error(error_msg)
        return False, error_msg
    
    except Exception as e:
        error_msg = f"Unexpected error: {str(e)}"
        logger.error(error_msg)
        return False, error_msg

def send_webhook_notification(entry_id: str, content: str, date_entry: str) -> Tuple[bool, str]:
    """
    Send webhook notification after a journal entry is added or updated.
    
    Args:
        entry_id (str): ID of the journal entry
        content (str): Content of the journal entry
        date_entry (str): Date of the journal entry in ISO format (YYYY-MM-DD)
    
    Returns:
        Tuple[bool, str]: Success status and response message or error
    """
    # Get webhook credentials from authentication module
    _, update_url, bearer_token = get_webhook_credentials()
    
    headers = {
        "Authorization": f"Bearer {bearer_token}",
        "Content-Type": "application/json"
    }
    
    # Structure the payload with a body wrapper as per requirements
    payload = {
        "body": {
            "date-entry": date_entry,
            "entry": content
        }
    }
    
    try:
        logger.info(f"Sending webhook notification for entry {entry_id} on date {date_entry}")
        response = requests.post(update_url, json=payload, headers=headers)
        response.raise_for_status()  # Raise exception for 4XX/5XX status codes
        
        return True, "Webhook notification sent successfully"
    
    except requests.exceptions.RequestException as e:
        error_msg = f"Webhook notification failed: {str(e)}"
        logger.error(error_msg)
        return False, error_msg
    
    except Exception as e:
        error_msg = f"Unexpected error in webhook notification: {str(e)}"
        logger.error(error_msg)
        return False, error_msg

def send_journal_entry(
    entry_text: str, 
    entry_date: str, 
    user_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    Send a journal entry to n8n for processing.
    
    Args:
        entry_text: The text content of the journal entry
        entry_date: The date of the journal entry (ISO format)
        user_id: Optional user ID for the entry
        
    Returns:
        Dictionary containing the response from n8n
    """
    chat_url, _, bearer_token = get_webhook_credentials()
    
    headers = {
        "Authorization": f"Bearer {bearer_token}",
        "Content-Type": "application/json"
    }
    
    data = {
        "type": "journal_entry",
        "content": entry_text,
        "date": entry_date,
    }
    
    if user_id:
        data["user_id"] = user_id
    
    try:
        logger.info(f"Sending journal entry from date {entry_date} to n8n")
        response = requests.post(chat_url, json=data, headers=headers, timeout=10)
        response.raise_for_status()
        
        try:
            return response.json()
        except json.JSONDecodeError:
            logger.error(f"Failed to parse n8n response as JSON: {response.text[:100]}...")
            return {"error": "Invalid JSON response", "raw_response": response.text}
            
    except requests.exceptions.RequestException as e:
        logger.error(f"Error communicating with n8n webhook: {str(e)}")
        if isinstance(e, requests.Timeout):
            return {"error": f"Request to n8n webhook timed out"}
        return {"error": f"Failed to connect to n8n webhook: {str(e)}"}
