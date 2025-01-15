import os
import streamlit as st
from pydub import AudioSegment
import speech_recognition as sr
from textblob import TextBlob

def transcribe_audio(mp3_file):
    """
    Converts MP3 audio to text using speech recognition.
    """
    # Convert MP3 to WAV
    audio = AudioSegment.from_mp3(mp3_file)
    wav_file = mp3_file.replace(".mp3", ".wav")
    audio.export(wav_file, format="wav")
    
    # Initialize recognizer
    recognizer = sr.Recognizer()
    with sr.AudioFile(wav_file) as source:
        audio_data = recognizer.record(source)
        try:
            text = recognizer.recognize_google(audio_data)
            return text
        except sr.UnknownValueError:
            return "Audio could not be understood."
        except sr.RequestError as e:
            return f"Speech Recognition service error: {e}"

def analyze_sentiment(transcription):
    """
    Analyzes sentiment of the transcription.
    Returns a sentiment score and polarity (positive/negative).
    """
    blob = TextBlob(transcription)
    sentiment_score = blob.sentiment.polarity
    sentiment_category = "Positive" if sentiment_score > 0 else "Negative" if sentiment_score < 0 else "Neutral"
    return sentiment_score, sentiment_category

def evaluate_keywords(transcription, keywords):
    """
    Evaluates the presence of key phrases in the transcription.
    Returns a keyword match score.
    """
    transcription_words = transcription.lower().split()
    keyword_count = sum(1 for word in keywords if word.lower() in transcription_words)
    return keyword_count / len(keywords) * 100 if keywords else 0

# Streamlit app
st.title("Customer Service Audio Analysis")
st.write("Upload an MP3 file to analyze its content.")

# File uploader
uploaded_file = st.file_uploader("Choose an MP3 file", type="mp3")

# Keywords input
keywords_input = st.text_input("Enter keywords (comma-separated):", "hello", "thank", "help", "please", "good", "bye", "resolved", "welcome")
keywords = [keyword.strip() for keyword in keywords_input.split(",")]

if uploaded_file is not None:
    # Save uploaded file locally
    with open(uploaded_file.name, "wb") as f:
        f.write(uploaded_file.read())

    # Transcribe and analyze audio
    st.write("Processing audio...")
    transcription = transcribe_audio(uploaded_file.name)
    if "Audio could not be understood" in transcription:
        st.error("Error in transcription. Please try another file.")
    else:
        sentiment_score, sentiment_category = analyze_sentiment(transcription)
        keyword_score = evaluate_keywords(transcription, keywords)

        # Display results
        st.subheader("Evaluation Results")
        st.write(f"**Transcription:** {transcription}")
        st.write(f"**Sentiment Score:** {sentiment_score:.2f} ({sentiment_category})")
        st.write(f"**Keyword Match Score:** {keyword_score:.2f}%")

        overall_score = (sentiment_score * 100 + keyword_score)
        st.write(f"**Overall Performance Score:** {overall_score:.2f}")

    # Clean up temporary file
    os.remove(uploaded_file.name)
