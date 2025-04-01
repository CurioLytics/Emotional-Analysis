import matplotlib.pyplot as plt

# Create Pie Chart
def create_pie_chart(emotions):
    fig, ax = plt.subplots()
    ax.pie(emotions.values(), labels=emotions.keys(), autopct="%1.1f%%", startangle=90)
    ax.axis("equal")  # Equal aspect ratio ensures pie is circular
    return fig

# Create Line Graph
def create_line_chart(emotions_df):
    fig, ax = plt.subplots()
    for emotion in emotions_df.columns:
        ax.plot(emotions_df.index, emotions_df[emotion], label=emotion)
    
    ax.set_xlabel("Day of the Week")
    ax.set_ylabel("Emotion Score")
    ax.legend()
    return fig
