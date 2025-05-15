"""
Chat with the AI about your journal
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
    """Generate a unique session ID"""
    return str(uuid.uuid4())

def main() -> None:
    """Chat page"""
    st.title("Let's chat! 💬")
    
    # Add a brief description
    st.markdown("""
    Hey girl! Let's talk about anything - your day, your journal, whatever's on your mind!
    """)
    
    # Initialize session state
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "session_id" not in st.session_state:
        st.session_state.session_id = generate_session_id()
    if "show_confirmation" not in st.session_state:
        st.session_state.show_confirmation = False
    
    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])
    
    # User input
    user_input = st.chat_input("Spill the tea...")
    
    if user_input:
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.write(user_input)
        
        # Create a placeholder for the assistant's response with a typing indicator
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            message_placeholder.markdown("Hmm...")
            
            # Get LLM response
            success, llm_response = send_message_to_llm(st.session_state.session_id, user_input)
            
            if not success:
                # If there was an error, show an error message
                error_message = f"Oops! {llm_response}"
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
    
    # Add a button to exit the chat
    if not st.session_state.show_confirmation:
        if st.button("Gotta go!"):
            if len(st.session_state.messages) > 0:
                st.session_state.show_confirmation = True
                st.rerun()
            else:
                # If no messages, simply clear and refresh
                st.session_state.messages = []
                st.session_state.session_id = generate_session_id()
                st.rerun()
    
    # Show confirmation dialog when the exit button is clicked
    if st.session_state.show_confirmation:
        # Create a container with a border and background for the popup effect
        with st.container():
            st.markdown("""
            <div style="padding:15px; border:1px solid #ddd; border-radius:5px; background-color:#f8f9fa;">
            <h4>Want me to save this as today's journal entry?</h4>
            </div>
            """, unsafe_allow_html=True)
            
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("Yes, save it!"):
                    # Send message to LLM to save conversation
                    with st.spinner("Saving to journal..."):
                        summary_success, summary_response = send_message_to_llm(
                            st.session_state.session_id, 
                            "Save my input as a journal entry for today."
                        )
                        
                        if summary_success:
                            st.success("All saved! ✨")
                        else:
                            st.error(f"Oops, couldn't save: {summary_response}")
                    
                    # Clear the session and create a new one
                    st.session_state.messages = []
                    st.session_state.session_id = generate_session_id()
                    st.session_state.show_confirmation = False
                    st.rerun()
            
            with col2:
                if st.button("Nah, just leave"):
                    # Just clear the session without saving
                    st.session_state.messages = []
                    st.session_state.session_id = generate_session_id()
                    st.session_state.show_confirmation = False
                    st.rerun()

def turn_to_journal():
    """Convert chat conversation to journal entry"""
    # This function will handle the process of converting
    # the chat conversation into a journal entry
    pass

if __name__ == "__main__":
    main()