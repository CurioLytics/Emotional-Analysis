# Remove unused os import since it's not needed in this test file
from utils.api_calls import get_random_quote, get_spotify_recommendations, get_exercise, get_summary

# Test quote function
print("Testing get_random_quote():")
print(get_random_quote())

# Test Spotify recommendations (mock data since we need API key)
print("\nTesting get_spotify_recommendations():")
test_emotions = {"happy": 0.7, "sad": 0.2, "angry": 0.1}
print(get_spotify_recommendations(test_emotions))

# Test exercise function (mock)
print("\nTesting get_exercise():")
print(get_exercise("happy"))

# Test summary function (mock)
print("\nTesting get_summary():")
test_text = "This week I felt productive on Monday but tired by Friday."
print(get_summary(test_text))