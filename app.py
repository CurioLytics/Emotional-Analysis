"""
Main entry point for the Journal Streamlit Application.

This application allows users to:
1. Create and manage journal entries
2. Analyze the emotional content of journal entries
3. Chat with an AI assistant about their journal memories
"""

import streamlit as st
import sys
from pathlib import Path
import logging
from datetime import datetime

# Add the project root to Python path
project_root = Path(__file__).parent.absolute()
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# Import utility functions if needed
from utils.auth import get_supabase_client

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    """Main function for the home page of the Journal application."""
    # Set up page configuration
    st.set_page_config(
        page_title="Journal App",
        page_icon="📓",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Display app title and description
    st.title("Journal Application")
    
    # Add a welcome message
    st.markdown("""
    ## Welcome to your personal journal app!
    
    This application allows you to:
    
    - **Create and manage journal entries** - Record your thoughts, feelings, and experiences
    - **Analyze the emotional content** of your journal entries with interactive visualizations
    - **Chat with an AI assistant** about your journal memories and insights
    
    Use the sidebar to navigate to different sections of the application.
    """)
    
    # Add app statistics
    st.subheader("App Overview")
    
    # Try to get journal entry count from Supabase
    try:
        supabase = get_supabase_client()
        response = supabase.table("documents").select("count", count="exact").execute()
        entry_count = response.count if hasattr(response, 'count') else 0
    except Exception as e:
        logger.error(f"Error fetching entry count: {str(e)}")
        entry_count = 0
    
    # Display app stats in columns
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(label="Journal Entries", value=entry_count)
    
    with col2:
        # Today's date for the "Days Journaling" metric
        today = datetime.now().strftime("%Y-%m-%d")
        st.metric(label="Today's Date", value=today)
    
    with col3:
        # Current version of the app
        st.metric(label="App Version", value="1.0.0")
    
    # Add a getting started section
    st.subheader("Getting Started")
    st.markdown("""
    1. **Journal Page**: Add a new journal entry for today or any date
    2. **Analysis Page**: View emotional analysis of your journal entries over time
    3. **Chat Page**: Talk to an AI assistant that can help you reflect on your journal entries
    
    Start by adding your first journal entry in the Journal Page.
    """)
    
    # Add a footer
    st.markdown("---")
    st.markdown("*Powered by Streamlit - Supabase - n8n - and Team9*")

if __name__ == "__main__":
    main()