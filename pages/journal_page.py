"""
Your journal entries
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
    """Get Supabase connection"""
    try:
        return get_supabase_client()
    except (ValueError, ConnectionError) as e:
        logger.error(str(e))
        st.error(str(e))
        st.stop()

def get_journal_entries():
    """Get all journal entries"""
    supabase = init_supabase()
    response = supabase.table("documents").select("id,date-entry,content").order("date-entry", desc=True).execute()
    
    if len(response.data) > 0:
        df = pd.DataFrame(response.data)
        df.rename(columns={"date-entry": "date", "content": "text"}, inplace=True)
        return df
    else:
        return pd.DataFrame({"id": [], "date": [], "text": []})

def get_journal_entry_by_date(date) -> Optional[Dict[str, Any]]:
    """Get entry for a specific date"""
    supabase = init_supabase()
    date_str = date.isoformat()
    response = supabase.table("documents").select("*").eq("date-entry", date_str).execute()
    return response.data[0] if len(response.data) > 0 else None

def add_journal_entry(date, text) -> Tuple[bool, Optional[str]]:
    """Add new entry"""
    supabase = init_supabase()
    
    entry = {
        "date-entry": date.isoformat(),
        "content": text
    }

    response = supabase.table("documents").insert(entry).execute()
    
    if len(response.data) > 0:
        return True, response.data[0].get("id")
    else:
        return False, None

def update_journal_entry(date, text) -> Tuple[bool, Optional[str]]:
    """Update existing entry"""
    supabase = init_supabase()
    date_str = date.isoformat()
    response = supabase.table("documents").update({"content": text}).eq("date-entry", date_str).execute()
    
    if len(response.data) > 0:
        return True, response.data[0].get("id")
    else:
        return False, None

def save_or_update_journal_entry(date, text) -> Tuple[bool, Optional[str], bool]:
    """Save or update entry"""
    existing_entry = get_journal_entry_by_date(date)
    
    if existing_entry:
        success, entry_id = update_journal_entry(date, text)
        return success, entry_id, True
    else:
        success, entry_id = add_journal_entry(date, text)
        return success, entry_id, False

def main():
    """Journal page"""
    st.title("Your Journal 📝")
    
    # Date picker and Add button in the same row
    col1, col2 = st.columns([3, 1])
    
    with col1:
        selected_date = st.date_input("Pick a date", datetime.now())
        
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
        st.write("")  # Add some space to align with date picker
        add_button = st.button("✏️ Write")
    
    # Container for the table
    st.subheader("Your stories so far")
    
    # Load data from Supabase
    with st.spinner("Loading your entries..."):
        df = get_journal_entries()
    
    # Create and display the DataFrame
    if not df.empty:
        if 'date' in df.columns:
            df['date'] = pd.to_datetime(df['date']).dt.strftime('%Y-%m-%d')
        
        st.dataframe(df[['date', 'text']], use_container_width=True)
    else:
        st.info("No entries yet. Time to start your story!")
    
    # Button click handler
    if add_button:
        st.session_state.show_entry_form = True
        
    # Show entry form if button was clicked
    if st.session_state.get('show_entry_form', False):
        with st.form("journal_entry_form"):
            initial_text = st.session_state.get("existing_entry_content", "")
            is_update = bool(initial_text)
            
            heading = f"{'Update' if is_update else 'New'} entry: {selected_date.strftime('%Y-%m-%d')}"
            st.write(heading)
            
            journal_text = st.text_area("What's on your mind?", value=initial_text, height=150)
            
            col1, col2 = st.columns([1, 3])
            with col1:
                submit_button = st.form_submit_button("Save")
            with col2:
                if st.form_submit_button("Nevermind"):
                    st.session_state.show_entry_form = False
                    st.rerun()
            
            if submit_button and journal_text:
                with st.spinner(f"{'Updating' if is_update else 'Saving'} entry..."):
                    success, entry_id, was_update = save_or_update_journal_entry(selected_date, journal_text)
                
                if success and entry_id:
                    date_str = selected_date.isoformat()
                    webhook_success, webhook_msg = send_webhook_notification(entry_id, journal_text, date_str)
                    
                    if not webhook_success:
                        st.warning(f"Saved but couldn't analyze it: {webhook_msg}")
                    
                    st.success(f"All done! ✨")
                    st.session_state.show_entry_form = False
                    st.rerun()
                else:
                    st.error(f"Oops, couldn't save. Try again?")

if __name__ == "__main__":
    main()