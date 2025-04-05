import ollama
from langdetect import detect
import tempfile
import whisper
import torch
from flask import Flask, request, jsonify
from deep_translator import GoogleTranslator
from moviepy import VideoFileClip
import os
import google.generativeai as genai
from dotenv import load_dotenv

# Load API key
load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Determine transcript file
translated_file = "translated_transcript.txt" if os.path.exists("translated_transcript.txt") else "translated.txt"

app = Flask(__name__)

# Language options
LANG_OPTIONS = {
    "English": "en",
    "Hindi": "hi",
    "Bengali": "bn",
    "Tamil": "ta",
    "Telugu": "te",
    "Marathi": "mr",
    "Gujarati": "gu",
    "Kannada": "kn",
    "Malayalam": "ml",
    "Punjabi": "pa",
    "Urdu": "ur"
}

# Load Whisper Model
device = "cuda" if torch.cuda.is_available() else "cpu"
model = whisper.load_model("small", device=device)


def read_transcript():
    """Read the translated transcript."""
    if os.path.exists(translated_file):
        with open(translated_file, "r", encoding="utf-8") as file:
            return file.read()
    else:
        st.error("No translated transcript file found!")
        return None


# Generate quizzes using AI
def generate_quiz(text):
    """Generate a structured quiz."""
    prompt = """
    You are an educational assistant. Create a multiple-choice quiz from the text.
    Provide exactly 5 questions, each with 4 options (A, B, C, D), and mark the correct answer separately.
    Keep the language the same as the input text.

    Format the output clearly like:
    1. Question text?
       A) Option 1
       B) Option 2
       C) Option 3
       D) Option 4

    After listing all 5 questions, provide the correct answers separately in this format:

    **Correct Answers:**
    1. X
    2. Y
    3. Z
    4. W
    5. V

    Text:
    """ + text

    model = genai.GenerativeModel("gemini-2.0-flash")
    response = model.generate_content(prompt)
    return response.text


# Generate structured exercises using AI
def generate_exercises(text):
    """Generate structured exercises without JSON."""
    prompt = """
    You are an educational assistant. Create structured exercises from the text.
    - 5 Fill-in-the-blank questions (missing words marked as '_____')
    - 5 Short-answer questions (1-2 sentence responses)
    - 5 Long-answer questions (detailed responses)

    Format the output clearly like:

    **Fill in the Blanks**
    1. Sentence with _____ missing.

    **Short Answer Questions**
    1. What is the importance of X?

    **Long Answer Questions**
    1. Explain how X impacts Y in detail.

    After listing all questions, provide the correct answers separately in this format:

    **Answers:**

    **Fill in the Blanks**
    1. Correct answer
    2. Correct answer

    **Short Answer Questions**
    1. Answer

    **Long Answer Questions**
    1. Answer

    Text:
    """ + text

    model = genai.GenerativeModel("gemini-2.0-flash")
    response = model.generate_content(prompt)
    return response.text


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
        return f"Translation Error: {str(e)}"


def detect_language(text):
    """Detects the language of the given text using langdetect."""
    try:
        return detect(text)
    except:
        return "en"  # Default to English if detection fails


def summarize_text(text, lang):
    """Summarizes the text and extracts key points in bullet format."""
    prompt = f"""  - Do not include general or repetitive sentences.
    Extract the most important points from the following text and format them into clear bullet points.
    The response should be in {lang}.
    - Use a structured format with bullet points. Keep it concise and include only essential information.
    """

    response = ollama.chat(model="llama3", messages=[
        {"role": "system", "content": prompt},
        {"role": "user", "content": text}
    ])

    # Ensure the response is a string
    summary = str(response["message"]["content"])

    return summary


def generate_flashcards(summary_text):
    """Formats the summary into structured flashcards."""
    flashcards = []

    # Ensure summary_text is a string
    summary_text = str(summary_text)

    points = summary_text.split("\n")

    for idx, point in enumerate(points, start=1):
        clean_point = point.strip()
        if clean_point:
            flashcards.append(f"📌 **Key Point {idx}:** {clean_point}")

    return "\n".join(flashcards)


def get_latest_transcript():
    """Determine which transcript file to use."""
    if os.path.exists("translated_transcript.txt") and os.path.getsize("translated_transcript.txt") > 0:
        return "translated_transcript.txt"
    elif os.path.exists("transcript.txt") and os.path.getsize("transcript.txt") > 0:
        return "transcript.txt"
    else:
        raise FileNotFoundError("No valid transcript found. Run transcription first.")


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"})


@app.route('/transcribe', methods=['POST'])
def transcribe_video():
    # Check if the post request has the file part
    if 'video' not in request.files:
        return jsonify({"error": "No video file provided"}), 400

    video_file = request.files['video']

    # Check if filename is empty
    if video_file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    # Get target language from form data (default to English if not provided)
    target_lang = request.form.get('target_language', 'English')

    # Validate target language
    if target_lang not in LANG_OPTIONS:
        return jsonify({"error": f"Invalid target language. Supported languages: {list(LANG_OPTIONS.keys())}"}), 400

    # Save uploaded file to a temporary location
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as temp_file:
        video_file.save(temp_file.name)
        video_path = temp_file.name

    try:
        # Extract audio
        audio_path = extract_audio(video_path)

        # Transcribe
        transcript = model.transcribe(audio_path)["text"]

        # Translate
        translated_text = translate_text(transcript, LANG_OPTIONS[target_lang])

        # Clean up temporary files
        os.unlink(video_path)
        os.unlink(audio_path)
        # Save original transcript
        with open("transcript.txt", "w", encoding="utf-8") as f:
            f.write(transcript)

        # Save translated transcript
        with open("translated_transcript.txt", "w", encoding="utf-8") as f:
            f.write(translated_text)

        # Return results as JSON
        return jsonify({
            "original_transcript": transcript,
            "translated_transcript": translated_text,
            "target_language": target_lang
        })

    except Exception as e:
        # Clean up temporary files in case of error
        if os.path.exists(video_path):
            os.unlink(video_path)
        if os.path.exists(audio_path):
            os.unlink(audio_path)

        return jsonify({"error": str(e)}), 500


@app.route('/summary', methods=['GET'])
def generate_summary():
    """Generate and return summary."""
    try:
        # Get the latest transcript
        transcript_file = get_latest_transcript()

        # Load text from transcript
        with open(transcript_file, "r", encoding="utf-8") as file:
            text = file.read()

        # Detect language
        detected_lang = detect_language(text)

        # Generate structured summary in bullet points
        summary_text = summarize_text(text, detected_lang)

        # Save Summary
        with open("summary.txt", "w", encoding="utf-8") as file:
            file.write(summary_text)

        return jsonify({
            "summary": summary_text,
            "language": detected_lang,
            "source_file": transcript_file
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/flashcards', methods=['GET'])
def generate_flashcards_route():
    """Generate and return flashcards."""
    try:
        # Get the latest transcript
        transcript_file = get_latest_transcript()

        # Load text from transcript
        with open(transcript_file, "r", encoding="utf-8") as file:
            text = file.read()

        # Detect language
        detected_lang = detect_language(text)

        # Generate structured summary in bullet points
        summary_text = summarize_text(text, detected_lang)

        # Generate flashcards
        flashcards = generate_flashcards(summary_text)

        # Save Flashcards
        with open("flashcards.txt", "w", encoding="utf-8") as file:
            file.write(flashcards)

        return jsonify({
            "flashcards": flashcards,
            "language": detected_lang,
            "source_file": transcript_file
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/quiz', methods=['GET'])
def quiz_route():
    transcript_text = read_transcript()

    if not transcript_text:
        return jsonify({"error": "No translated transcript file found"}), 404

    quiz = generate_quiz(transcript_text)
    return quiz, 200, {'Content-Type': 'application/json'}


@app.route('/exercise', methods=['GET'])
def exercise_route():
    transcript_text = read_transcript()

    if not transcript_text:
        return jsonify({"error": "No translated transcript file found"}), 404

    exercises = generate_exercises(transcript_text)
    return exercises, 200, {'Content-Type': 'application/json'}


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5003)