import requests
import os
import json
from dotenv import load_dotenv
import base64
# Load environment variables
load_dotenv()

# Get a real motivational quote from RapidAPI
def get_random_quote():
    """
    Fetches a random inspirational quote from RapidAPI.
    
    Returns:
        str: Formatted quote with author
    """
    import http.client
    
    conn = http.client.HTTPSConnection("quotes-inspirational-quotes-motivational-quotes.p.rapidapi.com")
    
    headers = {
        'x-rapidapi-key': os.getenv('RAPIDAPI_KEY'),
        'x-rapidapi-host': "quotes-inspirational-quotes-motivational-quotes.p.rapidapi.com"
    }
    
    try:
        conn.request("GET", "/quote?token=ipworld.info", headers=headers)
        res = conn.getresponse()
        data = res.read()
        quote_data = json.loads(data.decode("utf-8"))
        return f'"{quote_data["quote"]}" - {quote_data["author"]}'
    except Exception as e:
        print(f"Error fetching quote: {e}")
        return ""
    finally:
        conn.close()

# Get a playlist based on mood
import requests


def get_spotify_recommendations(emotion_pct, genre="pop", limit=5):

    SPOTIFY_API_URL = "https://api.spotify.com/v1/recommendations"

    # Mapping emotions to mood categories
    emotion_to_mood = {
        "joy": "happy",
        "anger": "energetic",
        "sadness": "sad",
        "fear": "relaxing",
        "disgust": "calm",
        "surprise": "uplifting",
        "neutral": "chill"
    }

    # Get the emotion with the highest percentage
    dominant_emotion = max(emotion_pct, key=emotion_pct.get)

    # Map emotion to mood (default to 'chill' if unknown)
    mood = emotion_to_mood.get(dominant_emotion, "chill")

    # Valence mapping (adjusted to fit Spotify's API)
    mood_valence = {
        "happy": 0.7,
        "sad": 0.3,
        "energetic": 0.8,
        "relaxing": 0.4,
        "calm": 0.5,
        "uplifting": 0.6,
        "chill": 0.5
    }

    params = {
        "seed_genres": genre,
        "min_valence": mood_valence.get(mood, 0.5),  # Default to neutral valence
        "limit": limit
    }

    access_token, refresh_token = get_spotify_access_token()
    if not access_token:
        return []
    headers = {"Authorization": f"Bearer {access_token}"}

    try:
        response = requests.get(SPOTIFY_API_URL, headers=headers, params=params)
        response.raise_for_status()
        tracks = response.json().get("tracks", [])

        return [{"name": t["name"], "artist": t["artists"][0]["name"], "url": t["external_urls"]["spotify"]} for t in tracks]

    except requests.exceptions.RequestException as e:
        print(f"Error fetching Spotify recommendations: {e}")
        return []

# Get exercise recommendation based on mood using YouTube Data API
def get_exercise(emotion):
    """
    Fetches exercise video recommendations from YouTube based on mood.
    Requires YOUTUBE_API_KEY in .env file.
    
    Args:
        emotion (str): Dominant emotion to search for
        
    Returns:
        str: URL of recommended exercise video
    """
    YOUTUBE_API = "https://www.googleapis.com/youtube/v3/search"
    
    # Map emotions to search queries
    emotion_to_query = {
        "joy": "happy workout",
        "anger": "anger management exercise",
        "sadness": "gentle yoga",
        "fear": "calming breathing exercises",
        "disgust": "mindfulness meditation",
        "surprise": "fun dance workout",
        "neutral": "beginner workout"
    }
    
    params = {

        "part": "snippet",
        "q": emotion_to_query.get(emotion, "workout"),
        "type": "video",
        "maxResults": 1,
        "key": os.getenv('YOUTUBE_API_KEY')
    }
    youtube_api_key = os.getenv('YOUTUBE_API_KEY')
    if not youtube_api_key:
        print("YouTube API key not found in environment variables")
        return ""
    
    try:
        response = requests.get(YOUTUBE_API, params=params)
        response.raise_for_status()
        items = response.json().get("items", [])
        if items:
            return f"https://www.youtube.com/watch?v={items[0]['id']['videoId']}"
        return ""
    except requests.exceptions.RequestException as e:
        print(f"Error fetching YouTube video: {e}")
        return ""

# Generate weekly summary using OpenAI API
def get_summary(user_text):
    """
    Generates a summary using OpenAI's API.
    Requires OPENAI_API_KEY in .env file.
    
    Args:
        user_text (str): Text to summarize
        
    Returns:
        str: Generated summary
    """
    prompt = "Summarize this weekly journal, focusing on the unique points. " \
             "Don't add any comments or suggestions, only analyze. Keep it under 50 words."
    
    OPENAI_API = "https://api.openai.com/v1/chat/completions"
    openai_key = os.getenv('OPENAI_API_KEY')
    if not openai_key:
        print("OpenAI API key not found in environment variables")
        return ""
    headers = {
        "Authorization": f"Bearer {openai_key}",
        "Content-Type": "application/json"
    }
    
    data = {
        "model": "gpt-3.5-turbo",
        "messages": [{"role": "user", "content": f"{prompt}: {user_text}"}],
        "temperature": 0.7,
        "max_tokens": 100
    }
    
    try:
        response = requests.post(OPENAI_API, json=data, headers=headers)
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]
    except requests.exceptions.RequestException as e:
        print(f"Error generating summary: {e}")
        return ""

def test_api_functions():
    while True:
        print("\nAPI Testing Menu:")
        print("1. Test Random Quote")
        print("2. Test Spotify Recommendations")
        print("3. Test Exercise Video")
        print("4. Test Weekly Summary")
        print("5. Exit")
        
        choice = input("\nEnter your choice (1-5): ")
        
        if choice == "1":
            quote = get_random_quote()
            print("\nRandom Quote:", quote)
            if not input("\nPress Enter to continue, or 'q' to quit: ").lower() == 'q':
                continue
            else:
                break
                
        elif choice == "2":
            emotion_pct = {"joy": 0.8, "sadness": 0.1, "anger": 0.1}
            songs = get_spotify_recommendations(emotion_pct)
            print("\nSpotify Recommendations:", songs)
            if not input("\nPress Enter to continue, or 'q' to quit: ").lower() == 'q':
                continue
            else:
                break
                
        elif choice == "3":
            exercise_url = get_exercise("joy")
            print("\nExercise Video URL:", exercise_url)
            if not input("\nPress Enter to continue, or 'q' to quit: ").lower() == 'q':
                continue
            else:
                break
                
        elif choice == "4":
            sample_text = "Had a great week. Accomplished all my tasks. Felt productive and happy."
            summary = get_summary(sample_text)
            print("\nWeekly Summary:", summary)
            if not input("\nPress Enter to continue, or 'q' to quit: ").lower() == 'q':
                continue
            else:
                break
                
        elif choice == "5":
            break
            
        else:
            print("\nInvalid choice. Please try again.")

if __name__ == "__main__":
    test_api_functions()
