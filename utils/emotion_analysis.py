from transformers import pipeline
import plotly.express as px

class EmotionAnalyzer:
    def __init__(self):
        self.classifier = pipeline(
            "text-classification",
            model="j-hartmann/emotion-english-distilroberta-base",
            top_k=1
        )

    def analyze_text(self, text):
        try:
            sentences = [s.strip() for s in text.split('.') if s.strip()]
            if not sentences:
                return {}, {}
                
            all_emotions = []
            emotion_counts = {}

            # Classify each sentence
            for sentence in sentences:
                result = self.classifier(sentence)
                emotion = result[0][0]['label']  # Extract top emotion
                
                all_emotions.append({
                    'sentence': sentence,
                    'emotion': emotion
                })

                # Track emotion counts
                emotion_counts[emotion] = emotion_counts.get(emotion, 0) + 1

            # Calculate emotion percentages
            total_sentences = len(all_emotions)
            percentages = {emotion: (count / total_sentences) * 100 for emotion, count in emotion_counts.items()}

            fig = px.pie(
                values=list(percentages.values()),
                names=list(percentages.keys()),
                title='Distribution of Emotions',
                labels={'names': 'Emotion', 'values': 'Percentage'},
                hole=0.3
            )
            return percentages, fig
            
        except Exception as e:
            print(f"Analysis error: {e}")
            return {}, None
