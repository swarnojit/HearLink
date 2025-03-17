import streamlit as st
import whisper
import tempfile
import os
from deep_translator import GoogleTranslator
from moviepy import VideoFileClip
import torch  # For GPU checking

# Ensure GPU is used if available
if not torch.cuda.is_available():
    st.error("❌ No GPU detected. Please use a CUDA-supported machine.")
else:
    st.success(f"✅ GPU detected: {torch.cuda.get_device_name(0)}")

# Load Whisper Model on GPU
model = whisper.load_model("small", device="cuda")

# Supported languages (Indian + English)
lang_options = {
    "English": "en",
    "Hindi (हिन्दी)": "hi",
    "Bengali (বাংলা)": "bn",
    "Tamil (தமிழ்)": "ta",
    "Telugu (తెలుగు)": "te",
    "Marathi (मराठी)": "mr",
    "Gujarati (ગુજરાતી)": "gu",
    "Kannada (ಕನ್ನಡ)": "kn",
    "Malayalam (മലയാളം)": "ml",
    "Punjabi (ਪੰਜਾਬੀ)": "pa",
    "Urdu (اردو)": "ur"
}

def extract_audio(video_path):
    """Extracts audio from a video file."""
    audio_path = video_path.replace(".mp4", ".wav")
    video = VideoFileClip(video_path)
    video.audio.write_audiofile(audio_path, codec="pcm_s16le")
    return audio_path

def translate_text(text, target_language):
    """Translates the transcribed text into the selected language."""
    try:
        return GoogleTranslator(source="auto", target=target_language).translate(text)
    except Exception as e:
        return f"❌ Translation Error: {str(e)}"

# Streamlit UI
st.title("🎥 Video Transcription & Translation 🇮🇳")

# Video Upload
uploaded_file = st.file_uploader("📤 Upload a Video File", type=["mp4", "avi", "mov", "mkv"])
if uploaded_file:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as temp_file:
        temp_file.write(uploaded_file.read())
        video_path = temp_file.name
    
    # Extract audio
    audio_path = extract_audio(video_path)
    
    # Transcribe
    transcript = model.transcribe(audio_path)["text"]

    # User selects translation language
    target_lang = st.selectbox("Select Language to Translate To", list(lang_options.keys()))
    translated_text = translate_text(transcript, lang_options[target_lang])

    # Display results
    st.text_area("📜 Original Transcript", transcript, height=200)
    st.text_area("📝 Translated Transcript", translated_text, height=200)

    # Save results to files
    with open("transcript.txt", "w", encoding="utf-8") as file:
        file.write(transcript)

    with open("translated_transcript.txt", "w", encoding="utf-8") as file:
        file.write(translated_text)

    st.success("✅ Transcription & Translation Completed! Saved as files.")
