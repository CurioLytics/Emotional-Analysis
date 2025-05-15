"""
Main app for the Journal
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
    """Main function for the app."""
    # Set up page configuration
    st.set_page_config(
        page_title="Journal App",
        page_icon="📓",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Display app title
    st.title("Hey there! 👋")
    
    # Add a welcome message
    st.markdown("""
    ## Good to see you back!
    
    What's up for today?
    
    - **Wanna write some thoughts?** 📝
    - **Curious about your mood these days?** 📊
    - **Wanna chat with me?** 💬
    """)
    
    # Add app statistics
    st.subheader("Quick Stats")
    
    # Try to get journal entry count from Supabase
    try:
        supabase = get_supabase_client()
        response = supabase.table("documents").select("count", count="exact").execute()
        entry_count = response.count if hasattr(response, 'count') else 0
    except Exception as e:
        logger.error(f"Error fetching entry count: {str(e)}")
        entry_count = 0
    
    # Display app stats in columns
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric(label="Your Entries", value=entry_count)
    
    with col2:
        today = datetime.now().strftime("%Y-%m-%d")
        st.metric(label="Today", value=today)
    
    # Add buttons for navigation
    st.markdown("### Where to?")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("[📝 Journal stuff](/journal_page)", unsafe_allow_html=True)
    with col2:
        st.markdown("[📊 How you've been feeling](/analysis_page)", unsafe_allow_html=True)
    with col3:
        st.markdown("[💬 Let's chat](/chat_page)", unsafe_allow_html=True)
    
    # Add a footer
    st.markdown("---")
    st.markdown("*Team9 vibes only ✨*")

if __name__ == "__main__":
    main()