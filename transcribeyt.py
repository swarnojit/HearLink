import streamlit as st
from dotenv import load_dotenv
import google.generativeai as genai
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound
import os
import base64

load_dotenv()  
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

def get_available_languages(video_id):
    """Fetch available transcript languages for a YouTube video."""
    try:
        transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
        return [t.language_code for t in transcript_list]
    except TranscriptsDisabled:
        return []
    except Exception:
        return []

def extract_transcript(youtube_video_url):
    """Fetch transcript in the original language."""
    try:
        video_id = youtube_video_url.split("=")[1]
        available_languages = get_available_languages(video_id)

        if not available_languages:
            return None, None

        transcript_text = YouTubeTranscriptApi.get_transcript(video_id, languages=[available_languages[0]])
        return " ".join([i["text"] for i in transcript_text]), available_languages[0]
    except NoTranscriptFound:
        return None, None
    except Exception as e:
        return None, str(e)

def transcribe_to_target_language(text, target_language):
    """Use Google Gemini to transcribe text into the target language."""
    model = genai.GenerativeModel("gemini-2.0-flash")
    response = model.generate_content(f"Transcribe this transcript into {target_language}:\n\n{text}")
    return response.text if response else text

def generate_detailed_notes(transcript_text, language):
    """Use Google Gemini to generate detailed notes from the transcript."""
    prompt = f"You are a YouTube video summarizer. Summarize the transcript into key points and detailed notes in {language}."
    model = genai.GenerativeModel("gemini-2.0-flash")
    response = model.generate_content(f"{prompt}\n\n{transcript_text}")
    return response.text if response else transcript_text

def save_text_to_file(text, filename):
    """Save text to a file."""
    with open(filename, "w", encoding="utf-8") as file:
        file.write(text)

def get_download_link(file_content, file_name, label):
    """Generate a download link for a file."""
    b64 = base64.b64encode(file_content.encode()).decode()
    return f'<a href="data:file/txt;base64,{b64}" download="{file_name}">{label}</a>'

st.title("YouTube Video Transcription & Notes Generator (With AI)")

youtube_link = st.text_input("Enter YouTube Video Link:")
target_language = st.selectbox(
    "Select Target Transcription Language:", 
    ["en", "hi", "ta", "bn", "te", "mr", "gu", "kn", "ml", "pa", "ur"]
)

if st.button("Get Transcription & Notes"):
    transcript_text, original_language = extract_transcript(youtube_link)

    if transcript_text is None:
        st.error("Could not retrieve transcript for this video in any language.")
    else:
        st.markdown(f"## Original Transcript (Language: {original_language.upper()})")
        st.write(transcript_text)

        # If the transcript is not in the target language, use AI to transcribe it
        if original_language != target_language:
            st.markdown(f"### Transcribing transcript from {original_language.upper()} to {target_language.upper()} using AI...")
            transcript_text = transcribe_to_target_language(transcript_text, target_language)
            file_name = "translated_transcribe.txt"
        else:
            file_name = "transcribe.txt"

        save_text_to_file(transcript_text, file_name)
        st.success(f"Saved transcription to `{file_name}`")

        # Generate download link for the transcript
        st.markdown(get_download_link(transcript_text, file_name, "📥 Download Transcription"), unsafe_allow_html=True)

        # Generate detailed notes
        st.markdown("### Generating Detailed Notes...")
        detailed_notes = generate_detailed_notes(transcript_text, target_language)
        save_text_to_file(detailed_notes, "detailed_notes.txt")
        st.success("Saved detailed notes to `detailed_notes.txt`")

        st.markdown("## Detailed Notes:")
        st.write(detailed_notes)

        # Generate download link for the detailed notes
        st.markdown(get_download_link(detailed_notes, "detailed_notes.txt", "📥 Download Detailed Notes"), unsafe_allow_html=True)
