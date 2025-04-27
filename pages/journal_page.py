"""
Journal entry module allowing users to create, view, and manage journal entries
that are stored in Supabase.
"""

import streamlit as st
import pandas as pd
from datetime import datetime
import uuid
import sys
import logging
from typing import Optional, Dict, Any, Tuple
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.parent.absolute()
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# Import utility functions
from utils.auth import get_supabase_client
from utils.webhook import send_webhook_notification

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def init_supabase():
    """
    Initialize Supabase client with credentials from environment variables.
    
    Returns:
        Any: Initialized Supabase client
        
    Raises:
        ValueError: If Supabase credentials are missing or invalid
        ConnectionError: If Supabase connection fails
    """
    try:
        # Use the centralized function for getting a Supabase client
        return get_supabase_client()
    except (ValueError, ConnectionError) as e:
        # Show the error in the Streamlit UI and stop execution
        error_msg = str(e)
        logger.error(error_msg)
        st.error(error_msg)
        st.stop()

# Function to fetch data from Supabase
def get_journal_entries():
    """
    Fetch journal entries from Supabase database.
    
    Returns:
        pd.DataFrame: DataFrame containing journal entries
    """
    supabase = init_supabase()
    # Updated to select only date-entry and content columns
    response = supabase.table("documents").select("id,date-entry,content").order("date-entry", desc=True).execute()
    
    if len(response.data) > 0:
        # Create DataFrame and rename columns for display
        df = pd.DataFrame(response.data)
        df.rename(columns={"date-entry": "date", "content": "text"}, inplace=True)
        return df
    else:
        return pd.DataFrame({"id": [], "date": [], "text": []})

# Function to get a specific journal entry by date
def get_journal_entry_by_date(date) -> Optional[Dict[str, Any]]:
    """
    Fetch a specific journal entry by date.
    
    Args:
        date (datetime): Date of the journal entry to fetch
        
    Returns:
        Optional[Dict[str, Any]]: The journal entry if found, None otherwise
    """
    supabase = init_supabase()
    
    # Format date as ISO string for the query
    date_str = date.isoformat()
    
    # Query for the specific date
    response = supabase.table("documents").select("*").eq("date-entry", date_str).execute()
    
    # Return the first entry if found, None otherwise
    return response.data[0] if len(response.data) > 0 else None

# Function to add a new journal entry
def add_journal_entry(date, text) -> Tuple[bool, Optional[str]]:
    """
    Add a new journal entry to the Supabase database.
    
    Args:
        date (datetime): Date of the journal entry
        text (str): Content of the journal entry
        
    Returns:
        Tuple[bool, Optional[str]]: Success status and entry ID if successful, None otherwise
    """
    supabase = init_supabase()
    
    entry = {
        "date-entry": date.isoformat(),
        "content": text
    }

    response = supabase.table("documents").insert(entry).execute()
    
    if len(response.data) > 0:
        # Return success status and entry ID
        return True, response.data[0].get("id")
    else:
        return False, None

# Function to update an existing journal entry
def update_journal_entry(date, text) -> Tuple[bool, Optional[str]]:
    """
    Update an existing journal entry in the Supabase database.
    
    Args:
        date (datetime): Date of the journal entry
        text (str): Updated content of the journal entry
        
    Returns:
        Tuple[bool, Optional[str]]: Success status and entry ID if successful, None otherwise
    """
    supabase = init_supabase()
    
    # Format date as ISO string for the query
    date_str = date.isoformat()
    
    response = supabase.table("documents").update({"content": text}).eq("date-entry", date_str).execute()
    
    if len(response.data) > 0:
        # Return success status and entry ID
        return True, response.data[0].get("id")
    else:
        return False, None

# Function to save or update a journal entry
def save_or_update_journal_entry(date, text) -> Tuple[bool, Optional[str], bool]:
    """
    Save a journal entry, updating if it already exists for the given date.
    
    Args:
        date (datetime): Date of the journal entry
        text (str): Content of the journal entry
        
    Returns:
        Tuple[bool, Optional[str], bool]: 
            - Success status
            - Entry ID if successful, None otherwise
            - Boolean indicating if it was an update (True) or new entry (False)
    """
    # Check if an entry already exists for this date
    existing_entry = get_journal_entry_by_date(date)
    
    if existing_entry:
        # Update existing entry
        success, entry_id = update_journal_entry(date, text)
        return success, entry_id, True
    else:
        # Create new entry
        success, entry_id = add_journal_entry(date, text)
        return success, entry_id, False

def main():
    """Main function for the journal entry page."""
    # Page title
    st.title("Journal Entry")
    
    # Date picker and Add button in the same row
    col1, col2 = st.columns([3, 1])
    
    with col1:
        selected_date = st.date_input("Select date", datetime.now())
        
        # Check if the date changed and if there's an existing entry
        if "last_selected_date" not in st.session_state or st.session_state.last_selected_date != selected_date:
            st.session_state.last_selected_date = selected_date
            existing_entry = get_journal_entry_by_date(selected_date)
            
            if existing_entry:
                st.session_state.existing_entry_content = existing_entry["content"]
                st.session_state.existing_entry_id = existing_entry["id"]
            else:
                st.session_state.existing_entry_content = ""
                st.session_state.existing_entry_id = None
    
    with col2:
        # Add button (positioned to align with the date picker)
        st.write("")  # Add some space to align with date picker
        add_button = st.button("+ Add")
    
    # Container for the table
    st.subheader("Journal Entries")
    
    # Load data from Supabase
    with st.spinner("Loading journal entries..."):
        df = get_journal_entries()
    
    # Create and display the DataFrame
    if not df.empty:
        # Format the date column if it exists
        if 'date' in df.columns:
            df['date'] = pd.to_datetime(df['date']).dt.strftime('%Y-%m-%d')
        
        # Display the dataframe
        st.dataframe(df[['date', 'text']], use_container_width=True)
    else:
        st.info("No journal entries found. Add your first entry!")
    
    # Button click handler
    if add_button:
        st.session_state.show_entry_form = True
        
    # Show entry form if button was clicked
    if st.session_state.get('show_entry_form', False):
        with st.form("journal_entry_form"):
            # Check if there's existing content for this date
            initial_text = st.session_state.get("existing_entry_content", "")
            is_update = bool(initial_text)
            
            # Change heading based on whether it's a new entry or an update
            heading = f"{'Update' if is_update else 'New'} entry for: {selected_date.strftime('%Y-%m-%d')}"
            st.write(heading)
            
            # Use the existing content as initial value if available
            journal_text = st.text_area("Journal entry", value=initial_text, height=150)
            
            col1, col2 = st.columns([1, 3])
            with col1:
                submit_button = st.form_submit_button("Save")
            with col2:
                if st.form_submit_button("Cancel"):
                    st.session_state.show_entry_form = False
                    st.rerun()
            
            if submit_button and journal_text:
                # Save or update entry in Supabase
                with st.spinner(f"{'Updating' if is_update else 'Saving'} entry..."):
                    success, entry_id, was_update = save_or_update_journal_entry(selected_date, journal_text)
                
                if success and entry_id:
                    # Send webhook notification with date
                    date_str = selected_date.isoformat()
                    webhook_success, webhook_msg = send_webhook_notification(entry_id, journal_text, date_str)
                    
                    if not webhook_success:
                        st.warning(f"Entry saved but webhook notification failed: {webhook_msg}")
                    
                    st.success(f"Entry {'updated' if was_update else 'saved'} successfully!")
                    st.session_state.show_entry_form = False
                    st.rerun()
                else:
                    st.error(f"Failed to {'update' if is_update else 'save'} entry. Please try again.")

if __name__ == "__main__":
    main()