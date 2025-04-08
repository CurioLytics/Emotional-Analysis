"""
Chat interface module allowing users to interact with an AI assistant
that can access and recall information from their journal entries.
"""

import streamlit as st
import uuid
import time
import sys
from typing import List, Dict, Any, Tuple
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.parent.absolute()
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# Import utility functions
from utils.webhook import send_message_to_llm

def generate_session_id() -> str:
    """
    Generate a unique session ID for the chat conversation.
    
    Returns:
        str: Unique UUID for the session
    """
    return str(uuid.uuid4())

def main() -> None:
    """Main function for the chat interface page."""
    st.title("Chat with yourself")
    
    # Add a brief description
    st.markdown("""
    This chat interface allows you to interact with an AI assistant that can 
    recall information from your journal entries. Ask questions about past events,
    feelings, or memories you've recorded.
    """)
    
    # Initialize session state
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "session_id" not in st.session_state:
        st.session_state.session_id = generate_session_id()
    
    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])
    
    # User input
    user_input = st.chat_input("Wanna get your memories, or anything in mind?...")
    
    if user_input:
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.write(user_input)
        
        # Create a placeholder for the assistant's response with a typing indicator
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            message_placeholder.markdown("Thinking...")
            
            # Get LLM response
            success, llm_response = send_message_to_llm(st.session_state.session_id, user_input)
            
            if not success:
                # If there was an error, show an error message
                error_message = f"Error: {llm_response}"
                message_placeholder.error(error_message)
                st.session_state.messages.append({"role": "assistant", "content": error_message})
            else:
                # Simulate typing effect for better UX
                full_response = llm_response
                response_parts = full_response.split()
                
                displayed_message = ""
                for i, word in enumerate(response_parts):
                    displayed_message += word + " "
                    if i % 3 == 0 or i == len(response_parts) - 1:  # Update every few words
                        message_placeholder.markdown(displayed_message)
                        time.sleep(0.05)  # Small delay for typing effect
                
                # Final display of the complete message
                message_placeholder.markdown(full_response)
                
                # Add LLM response to chat history
                st.session_state.messages.append({"role": "assistant", "content": full_response})
    
    # Add a button to clear the chat history
    if st.button("Clear conversation"):
        st.session_state.messages = []
        st.session_state.session_id = generate_session_id()
        st.rerun()

if __name__ == "__main__":
    main()