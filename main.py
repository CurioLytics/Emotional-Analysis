import streamlit as st
import pandas as pd
from utils.emotion_analysis import classify_emotions
from utils.api_calls import get_random_quote, get_playlist, get_exercise, get_summary
from utils.visualization import create_pie_chart, create_line_chart

# Sidebar Navigation
st.sidebar.title("Navigation")
analysis_type = st.sidebar.radio("Choose Analysis", ["Daily Analysis", "Weekly Analysis"])

# Get Input (Text or File)
st.title("📊 Emotional Analyzer")
input_method = st.radio("How would you like to provide input?", ["Type Text", "Upload File"])

if input_method == "Type Text":
    user_text = st.text_area("Enter your text here:")
elif input_method == "Upload File":
    uploaded_file = st.file_uploader("Upload a text file", type=["txt"])
    if uploaded_file:
        user_text = uploaded_file.read().decode("utf-8")
else:
    user_text = ""

# Proceed if input is provided
if user_text:
    if analysis_type == "Daily Analysis":
        st.subheader("📅 Daily Emotional Analysis")
        
        # Emotion Classification
        analyzer = EmotionAnalyzer()
        result = analyzer.analyze_text(user_text)
        emotion_pct=result[0]
        dominant_emotion = max(emotion_pct, key=emotion_pct.get)
        st.write(f"Emotion Percentages: {emotion_pct}")
        pie_chart = create_pie_chart(emotion_pct)
        st.pyplot(pie_chart)

        
        # API Calls for Recommendations
        quote = get_random_quote()
        st.write(f"📜 Quote for the Day: {quote}")

        playlist = get_playlist(dominant_emotion)
        st.write(f"🎶 Recommended Playlist: {playlist}")

        exercise = get_exercise(dominant_emotion)
        st.write(f"🏋️ Suggested Exercise: {exercise}")

    elif analysis_type == "Weekly Analysis":
        st.subheader("📆 Weekly Emotional Analysis")

        # Emotion Classification
        analyzer = EmotionAnalyzer()
        result = analyzer.analyze_text(user_text)
        emotion_pct=result[0]
        dominant_emotion = max(emotion_pct, key=emotion_pct.get)
        st.write(f"Emotion Percentages: {emotion_pct}")
        pie_chart = create_pie_chart(emotion_pct)
        st.pyplot(pie_chart)

        # AI-generated Weekly Summary
        summary = get_summary(user_text)
        st.write(f"📝 Weekly Summary: {summary}")

