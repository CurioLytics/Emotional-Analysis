"""
Journal analysis module that displays emotional analysis data from journal entries
stored in Supabase.

This module provides visualizations and insights into the emotional content
of journal entries, including line graphs and pie charts showing emotion trends.
"""

import streamlit as st
import pandas as pd
import altair as alt
import plotly.express as px
from datetime import datetime, timedelta
import sys
import logging
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.parent.absolute()
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# Import utility functions
from utils.auth import get_supabase_client

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Define emotion columns based on the database schema
EMOTION_COLUMNS = ["joy", "sadness", "love", "anger", "fear", "surprise"]

# Define emotion emojis mapping
EMOTION_EMOJIS = {
    "joy": "😊",
    "sadness": "😢",
    "love": "❤️",
    "anger": "😡",
    "fear": "😨",
    "surprise": "😲"
}

# Define emotion ratios for score calculation
# Positive emotions have positive ratios, negative emotions have negative ratios
EMOTION_RATIOS = {
    "joy": 1.0,    # Highly positive
    "love": 0.8,   # Positive
    "surprise": 0.5,     # Mildly positive
    "fear": -0.5,        # Mildly negative
    "sadness": -0.8,     # Negative
    "anger": -0.9,       # Strongly negative
}

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

def generate_dummy_data() -> pd.DataFrame:
    """
    Generate dummy emotion data for testing purposes.
    
    Returns:
        pd.DataFrame: DataFrame with 10 rows of simulated journal entries and emotion scores
    """
    # Create date range for the past 10 days
    today = datetime.now()
    dates = [(today - timedelta(days=i)).date() for i in range(10)]
    dates.reverse()  # Order from oldest to newest
    
    # Sample journal content snippets
    contents = [
        "Today was a wonderful day. I felt really happy and accomplished.",
        "Feeling a bit down today. Nothing seems to be going right.",
        "I'm anxious about the upcoming presentation. Hope it goes well.",
        "I can't believe what happened! I'm so angry right now.",
        "Not much happened today. Just a regular day at work.",
        "Something unexpected happened and it took me by surprise!",
        "That movie was disgusting. I regret watching it.",
        "Mixed feelings today. Happy about the promotion but sad about moving.",
        "Feeling peaceful and content with life right now.",
        "Today was frustrating, but I'm trying to stay positive."
    ]
    
    # Generate random emotion scores that make sense with the content
    emotion_data = [
        # Happy day
        {"joy": 0.8, "sadness": 0.1, "fear": 0.05, "anger": 0.02, "surprise": 0.2, "love": 0.1},
        # Sad day
        {"joy": 0.1, "sadness": 0.7, "fear": 0.2, "anger": 0.15, "surprise": 0.05, "love": 0.05},
        # Anxious day
        {"joy": 0.1, "sadness": 0.3, "fear": 0.75, "anger": 0.1, "surprise": 0.2, "love": 0.05},
        # Angry day
        {"joy": 0.05, "sadness": 0.2, "fear": 0.1, "anger": 0.85, "surprise": 0.3, "love": 0.05},
        # Neutral day
        {"joy": 0.2, "sadness": 0.2, "fear": 0.1, "anger": 0.1, "surprise": 0.1, "love": 0.05},
        # Surprised day
        {"joy": 0.4, "sadness": 0.1, "fear": 0.3, "anger": 0.05, "surprise": 0.9, "love": 0.1},
        # Disgusted day
        {"joy": 0.05, "sadness": 0.3, "fear": 0.2, "anger": 0.4, "surprise": 0.2, "love": 0.05},
        # Mixed emotions day
        {"joy": 0.6, "sadness": 0.5, "fear": 0.3, "anger": 0.1, "surprise": 0.4, "love": 0.2},
        # Content day
        {"joy": 0.7, "sadness": 0.05, "fear": 0.05, "anger": 0.05, "surprise": 0.1, "love": 0.3},
        # Frustrated but positive day
        {"joy": 0.4, "sadness": 0.3, "fear": 0.1, "anger": 0.5, "surprise": 0.15, "love": 0.1}
    ]
    
    # Create DataFrame
    data = []
    for i, date in enumerate(dates):
        entry = {
            "date-entry": pd.Timestamp(date),
            "content": contents[i],
        }
        # Add emotion scores
        entry.update(emotion_data[i])
        data.append(entry)
    
    return pd.DataFrame(data)

def get_emotion_scores(start_date: Optional[datetime] = None, 
                       end_date: Optional[datetime] = None) -> pd.DataFrame:
    """
    Fetch emotion scores from Supabase database within the given date range.
    
    The function queries the database for emotion scores and formats the data
    for visualization.
    
    Args:
        start_date (Optional[datetime]): Start date for filtering
        end_date (Optional[datetime]): End date for filtering
        
    Returns:
        pd.DataFrame: DataFrame containing emotion scores with date and columns
                     for each emotion (happiness, sadness, etc.)
    """
    # For testing purposes: uncomment the line below to use dummy data instead of actual data
    # return generate_dummy_data()
    
    supabase = init_supabase()
    EMOTIONS_TABLE = "documents" 
    try:
        # Start with a query to the emotions table using the correct table name
        query = supabase.table(EMOTIONS_TABLE).select("*")
        
        # Apply date filters if provided
        if start_date:
            query = query.gte("date-entry", start_date.isoformat())
        if end_date:
            query = query.lte("date-entry", end_date.isoformat())
        
        # Execute the query and order by date
        response = query.order("date-entry", desc=False).execute()
        
        if len(response.data) > 0:
            # Create DataFrame
            df = pd.DataFrame(response.data)
            
            # Convert date strings to datetime objects
            if 'date-entry' in df.columns:
                df['date-entry'] = pd.to_datetime(df['date-entry'])
                
            return df
        else:
            # Return empty DataFrame with expected columns
            empty_df = pd.DataFrame(columns=['date-entry'] + EMOTION_COLUMNS)
            empty_df['date-entry'] = pd.to_datetime(empty_df['date-entry'])
            return empty_df
    except Exception as e:
        # Log the error and show a message to the user
        error_msg = f"Error retrieving emotion data: {str(e)}"
        logger.error(error_msg)
        st.error(error_msg)
        
        # Return empty DataFrame
        empty_df = pd.DataFrame(columns=['date-entry'] + EMOTION_COLUMNS)
        return empty_df

def calculate_emotion_score(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate a single emotion score for each entry by applying emotion ratios.
    
    This function creates a new column 'emotion_score' which is the sum of each emotion
    value multiplied by its corresponding ratio (positive ratios for positive emotions,
    negative ratios for negative emotions).
    
    Args:
        df (pd.DataFrame): DataFrame containing emotion data with separate columns for each emotion
        
    Returns:
        pd.DataFrame: DataFrame with an additional 'emotion_score' column
    """
    if df.empty:
        return pd.DataFrame(columns=['date-entry', 'emotion_score'])
    
    # Create a copy to avoid modifying the original dataframe
    result_df = df.copy()
    
    # Initialize the emotion_score column
    result_df['emotion_score'] = 0.0
    
    # Calculate the emotion score as the sum of each emotion value multiplied by its ratio
    for emotion in EMOTION_COLUMNS:
        if emotion in result_df.columns:
            result_df['emotion_score'] += result_df[emotion] * EMOTION_RATIOS.get(emotion, 0.0)
    
    # Return DataFrame with only date and emotion_score columns
    return result_df[['date-entry', 'emotion_score']]

def display_emotion_line_chart(df: pd.DataFrame) -> None:
    """
    Display a line chart of combined emotion score over time.
    
    Args:
        df (pd.DataFrame): DataFrame containing emotion data
    """
    if df.empty:
        st.info("No emotion data available to display.")
        return
    
    # Calculate emotion score
    chart_df = calculate_emotion_score(df)
    
    # Create the chart with a single line
    chart = alt.Chart(chart_df).mark_line().encode(
        x=alt.X('date-entry:T', title='Date'),
        y=alt.Y('emotion_score:Q', title='Emotion Score'),
        tooltip=['date-entry', 'emotion_score']
    ).properties(
        title='Emotion Score Over Time',
        width=700,
        height=400
    ).interactive()
    
    # Add a zero line to indicate the neutral threshold
    zero_line = alt.Chart(pd.DataFrame({'y': [0]})).mark_rule(strokeDash=[3, 3], color='gray').encode(
        y='y'
    )
    
    # Combine the line chart with the zero line
    final_chart = chart + zero_line
    
    st.altair_chart(final_chart, use_container_width=True)

def display_emotion_pie_chart(df: pd.DataFrame) -> None:
    """
    Display a pie chart showing the distribution of emotions.
    
    Args:
        df (pd.DataFrame): DataFrame containing emotion data
    """
    if df.empty:
        st.info("No emotion data available to display.")
        return
    
    # Calculate average values for each emotion across the selected date range
    emotion_means = {emotion: df[emotion].mean() for emotion in EMOTION_COLUMNS if emotion in df.columns}
    
    # Create a DataFrame for the pie chart
    pie_data = pd.DataFrame({
        'emotion': list(emotion_means.keys()),
        'average_score': list(emotion_means.values())
    })
    
    # Create the pie chart using Plotly
    fig = px.pie(
        pie_data, 
        values='average_score', 
        names='emotion',
        title='Emotion Distribution',
        color_discrete_sequence=px.colors.qualitative.Plotly,
        labels={'emotion': 'Emotion', 'average_score': 'Average Score'}
    )
    
    # Update trace settings for better appearance
    fig.update_traces(
        textposition='inside', 
        textinfo='percent+label',
        hole=0.3,  # Creates a donut chart effect
        pull=[0.05 if emotion == pie_data['average_score'].idxmax() else 0 for emotion in range(len(pie_data))]
    )
    
    st.plotly_chart(fig, use_container_width=True)

def get_emotion_summary(df: pd.DataFrame) -> Dict[str, float]:
    """
    Calculate average scores for each emotion.
    
    Args:
        df (pd.DataFrame): DataFrame containing emotion data
        
    Returns:
        Dict[str, float]: Dictionary mapping emotions to their average scores
    """
    if df.empty:
        return {}
    
    # Calculate mean for each emotion column
    summary = {emotion: df[emotion].mean() for emotion in EMOTION_COLUMNS if emotion in df.columns}
    return summary

def calculate_dominant_emotion(df: pd.DataFrame) -> Tuple[str, float]:
    """
    Determine the dominant emotion based on average scores.
    
    Args:
        df (pd.DataFrame): DataFrame containing emotion data
        
    Returns:
        Tuple[str, float]: Tuple containing the name of the dominant emotion and its score
    """
    if df.empty:
        return ("", 0.0)
    
    # Get average score for each emotion
    emotion_summary = get_emotion_summary(df)
    
    # Find the emotion with the highest average score
    if emotion_summary:
        dominant_emotion = max(emotion_summary.items(), key=lambda x: x[1])
        return dominant_emotion
    
    return ("", 0.0)

def add_main_emotion_column(df: pd.DataFrame) -> pd.DataFrame:
    """
    Add a main_emotion column to the DataFrame containing the dominant emotion for each entry.
    
    Args:
        df (pd.DataFrame): DataFrame containing emotion data
        
    Returns:
        pd.DataFrame: DataFrame with an additional main_emotion column
    """
    if df.empty or not any(col in df.columns for col in EMOTION_COLUMNS):
        return df
    
    # Create a copy to avoid modifying the original dataframe
    result_df = df.copy()
    
    # For each row, find the emotion with the highest score
    def get_max_emotion(row):
        emotions_only = {emotion: row[emotion] for emotion in EMOTION_COLUMNS if emotion in row}
        if emotions_only:
            return max(emotions_only.items(), key=lambda x: x[1])[0]
        return ""
    
    # Apply the function to each row
    result_df['main_emotion'] = result_df.apply(get_max_emotion, axis=1)
    
    return result_df

def main():
    """Main function for the journal analysis page."""
    # Page title
    st.title("Journal Analysis")
    
    st.write("""
    This page displays emotional analysis of your journal entries.
    The analysis shows the distribution and trends of emotions detected in your writing over time.
    The line chart displays an overall emotion score where positive values indicate positive emotions
    and negative values indicate negative emotions.
    """)
    
    # Date filter controls
    st.subheader("Filter by Date")
    
    # Get all available dates from the database
    all_data = get_emotion_scores()
    
    if not all_data.empty and 'date-entry' in all_data.columns:
        # Extract min and max dates from the data
        min_date = all_data['date-entry'].min().date()
        max_date = all_data['date-entry'].max().date()
        
        # Set default dates (last 30 days)
        default_start = max(min_date, (datetime.now() - timedelta(days=30)).date())
        default_end = max_date
        
        # Use date range slider instead of date pickers
        date_range = st.slider(
            "Select Date Range",
            min_value=min_date,
            max_value=max_date,
            value=(default_start, default_end),
            format="YYYY-MM-DD"
        )
        
        # Unpack the selected date range
        start_date, end_date = date_range
    else:
        # Fallback to date pickers if no data is available
        default_start = (datetime.now() - timedelta(days=30)).date()
        default_end = datetime.now().date()
        
        col1, col2 = st.columns(2)
        with col1:
            start_date = st.date_input("Start Date", default_start)
        with col2:
            end_date = st.date_input("End Date", default_end)
    
    # Convert date inputs to datetime objects
    start_datetime = datetime.combine(start_date, datetime.min.time())
    end_datetime = datetime.combine(end_date, datetime.max.time())
    
    # Add a checkbox to use dummy data for testing
    use_dummy_data = st.sidebar.checkbox("Use dummy test data", value=False)
    
    # Fetch emotion data based on date filter
    with st.spinner("Loading emotion data..."):
        if use_dummy_data:
            emotion_df = generate_dummy_data()
            # Filter based on date range if needed
            if start_datetime and end_datetime:
                emotion_df = emotion_df[
                    (emotion_df['date-entry'] >= pd.Timestamp(start_datetime)) & 
                    (emotion_df['date-entry'] <= pd.Timestamp(end_datetime))
                ]
        else:
            emotion_df = get_emotion_scores(start_datetime, end_datetime)
    
    # Display charts and insights if data is available
    if not emotion_df.empty and any(col in emotion_df.columns for col in EMOTION_COLUMNS):
        # Create tabs for different visualizations
        tab1, tab2, tab3 = st.tabs(["Line Chart", "Pie Chart", "Data"])
        
        # Tab 1: Line Chart
        with tab1:
            st.subheader("Emotion Trends Over Time")
            st.write("""
            The line chart below shows your overall emotional state over time. 
            Positive values indicate positive emotions (happiness, surprise), 
            while negative values indicate negative emotions (sadness, fear, anger, disgust).
            Values near zero indicate neutral emotions.
            """)
            display_emotion_line_chart(emotion_df)
        
        # Tab 2: Pie Chart
        with tab2:
            st.subheader("Emotion Distribution")
            display_emotion_pie_chart(emotion_df)
        
        # Tab 3: Data Table
        with tab3:
            st.subheader("Raw Emotion Data")
            # Format the date column for display
            display_df = emotion_df.copy()
            
            # Add main_emotion column
            display_df = add_main_emotion_column(display_df)
            
            # Define the specific columns to display in the order requested
            columns_to_display = ['date-entry', 'content', 'main_emotion'] + EMOTION_COLUMNS
            
            # Filter to only include columns that exist in the dataframe
            display_df = display_df[[col for col in columns_to_display if col in display_df.columns]]
            
            # Rename date-entry to date for display
            if 'date-entry' in display_df.columns:
                display_df = display_df.rename(columns={'date-entry': 'date'})
                display_df['date'] = display_df['date'].dt.strftime('%Y-%m-%d')
            
            # Show the table with all requested columns
            st.dataframe(display_df, use_container_width=True)
        
        # Display summary statistics with emojis
        st.subheader("Emotion Summary")
        emotion_summary = get_emotion_summary(emotion_df)
        
        if emotion_summary:
            # Determine number of columns needed (max 3 emotions per row)
            num_emotions = len(emotion_summary)
            num_rows = (num_emotions + 2) // 3  # Ceiling division
            
            # Create a grid layout for emotion metrics
            for row in range(num_rows):
                cols = st.columns(3)
                for i in range(3):
                    idx = row * 3 + i
                    if idx < num_emotions:
                        emotion = list(emotion_summary.keys())[idx]
                        score = emotion_summary[emotion]
                        emoji = EMOTION_EMOJIS.get(emotion, "")
                        with cols[i]:
                            st.metric(
                                label=f"{emoji} {emotion.capitalize()}", 
                                value=f"{score:.2f}",
                                delta=None
                            )
            
            # Display the dominant emotion
            dominant_emotion, dominant_score = calculate_dominant_emotion(emotion_df)
            if dominant_emotion:
                emoji = EMOTION_EMOJIS.get(dominant_emotion, "")
                st.info(f"Your most prominent emotion during this period was **{emoji} {dominant_emotion.capitalize()}** with an average score of {dominant_score:.2f}.")
    else:
        st.info("No emotion data available for the selected date range. Try selecting a different period or adding more journal entries.")

if __name__ == "__main__":
    main()