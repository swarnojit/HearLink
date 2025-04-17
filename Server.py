import uuid
import ollama
from langdetect import detect
import whisper
import torch
from flask import Flask, request, jsonify, send_file
from deep_translator import GoogleTranslator
from moviepy import VideoFileClip
from youtube_transcript_api import YouTubeTranscriptApi, NoTranscriptFound, TranscriptsDisabled
from flask import Flask, request, jsonify
from dotenv import load_dotenv
import google.generativeai as genai
import os
import PyPDF2
import docx
import tempfile
from flask_cors import CORS

# Load API key
load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Determine transcript file
translated_file = "translated_transcript.txt" if os.path.exists("translated_transcript.txt") else "translated.txt"

app = Flask(__name__)
CORS(app)

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
    """Generate a structured quiz from the input text."""
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

    # Generate the quiz using the model
    model = genai.GenerativeModel("gemini-2.0-flash")
    response = model.generate_content(prompt)

    quiz_text = response.text.strip()

    # Parsing the generated quiz text
    quiz_questions = []
    correct_answers = {}

    # Extracting questions and answers
    try:
        # Split the questions and correct answers part
        questions_part, answers_part = quiz_text.split("**Correct Answers:**")

        # Process the questions part
        questions_lines = questions_part.strip().split("\n\n")
        for line in questions_lines:
            lines = line.strip().split("\n")
            question = lines[0].strip().replace("?", "")  # Remove the question mark
            options = [option.strip() for option in lines[1:]]  # Options A, B, C, D

            quiz_questions.append({
                "question": question,
                "options": options,
            })

        # Process the correct answers part
        answers_lines = answers_part.strip().split("\n")
        for i, line in enumerate(answers_lines):
            # The format should be something like "1. C"
            question_number, answer = line.strip().split(".")
            correct_answers[int(question_number)] = answer.strip()

        # Return the structured quiz format
        structured_quiz = []
        for i, question_data in enumerate(quiz_questions):
            structured_quiz.append({
                "question": question_data["question"],
                "options": question_data["options"],
                "answer": correct_answers.get(i + 1)  # Adding correct answer
            })

        return structured_quiz

    except Exception as e:
        return {"error": f"Error processing quiz: {str(e)}"}


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

    # Map language codes to language names for clarity in the prompt
    language_names = {
        "en": "English",
        "hi": "Hindi",
        "bn": "Bengali",
        "ta": "Tamil",
        "te": "Telugu",
        "mr": "Marathi",
        "gu": "Gujarati",
        "kn": "Kannada",
        "ml": "Malayalam",
        "pa": "Punjabi",
        "ur": "Urdu"
    }

    lang_name = language_names.get(lang, lang)

    prompt = f"""You are a multilingual assistant.

IMPORTANT: Your response MUST be in {lang_name} language ({lang}).
- DO NOT respond in English. Respond ONLY in {lang_name}.
- Extract only the most important points from the following text.
- Use clear and concise bullet points.
- Format your response in a structured, easy-to-read format.

Text to summarize:
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

    # Split by newline and filter out empty lines
    points = [point.strip() for point in summary_text.split("\n") if point.strip()]

    for idx, point in enumerate(points, start=1):
        flashcards.append(f"📌 **Key Point {idx}:** {point}")

    # Join the flashcards into a string and return
    return "\n".join(flashcards)


def get_latest_transcript():
    """Determine which transcript file to use."""
    if os.path.exists("translated_transcript.txt") and os.path.getsize("translated_transcript.txt") > 0:
        return "translated_transcript.txt"
    elif os.path.exists("transcript.txt") and os.path.getsize("transcript.txt") > 0:
        return "transcript.txt"
    else:
        raise FileNotFoundError("No valid transcript found. Run transcription first.")


@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"})


@app.route('/api/transcribe', methods=['POST'])
def transcribe_video():
    print("Received request...")
    print("Files:", request.files)
    print("Form data:", request.form)

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
            "target_language": target_lang,

        })

    except Exception as e:
        # Clean up temporary files in case of error
        if os.path.exists(video_path):
            os.unlink(video_path)
        if os.path.exists(audio_path):
            os.unlink(audio_path)

        return jsonify({"error": str(e)}), 500


@app.route('/api/summary', methods=['GET'])
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


@app.route('/api/flashcards', methods=['GET'])
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
        flashcard_list = [line.strip() for line in flashcards.strip().split("\n") if line.strip()]

        return jsonify({
            "flashcards": flashcard_list,
            "language": detected_lang,
            "source_file": transcript_file
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/quiz', methods=['GET'])
def quiz_route():
    transcript_text = read_transcript()

    if not transcript_text:
        return jsonify({"error": "No translated transcript file found"}), 404

    quiz = generate_quiz(transcript_text)
    return quiz, 200, {'Content-Type': 'application/json'}


import re


def parse_exercise_response(text):
    try:
        # Split main sections
        fill_blanks = re.findall(r'\*\*Fill in the Blanks\*\*\s*(.*?)\*\*Short Answer Questions\*\*', text, re.S)[
            0].strip()
        short_answers = re.findall(r'\*\*Short Answer Questions\*\*\s*(.*?)\*\*Long Answer Questions\*\*', text, re.S)[
            0].strip()
        long_answers = re.findall(r'\*\*Long Answer Questions\*\*\s*(.*?)\*\*Answers:\*\*', text, re.S)[0].strip()
        answers_section = re.findall(r'\*\*Answers:\*\*\s*(.*)', text, re.S)[0].strip()

        # Extract answers separately
        fb_answers = \
        re.findall(r'\*\*Fill in the Blanks\*\*\s*(.*?)\*\*Short Answer Questions\*\*', answers_section, re.S)[
            0].strip()
        sa_answers = \
        re.findall(r'\*\*Short Answer Questions\*\*\s*(.*?)\*\*Long Answer Questions\*\*', answers_section, re.S)[
            0].strip()
        la_answers = re.findall(r'\*\*Long Answer Questions\*\*\s*(.*)', answers_section, re.S)[0].strip()

        # Extract numbered items
        def extract_items(block):
            return [re.sub(r'^\d+\.\s*', '', line.strip()) for line in block.strip().split('\n') if line.strip()]

        return {
            "fillBlanks": extract_items(fill_blanks),
            "shortAnswer": extract_items(short_answers),
            "longAnswer": extract_items(long_answers),
            "answers": {
                "fillBlanks": extract_items(fb_answers),
                "shortAnswer": extract_items(sa_answers),
                "longAnswer": extract_items(la_answers)
            }
        }

    except Exception as e:
        print("Parsing error:", str(e))
        return None


@app.route('/api/exercise', methods=['GET'])
def exercise_route():
    transcript_text = read_transcript()

    if not transcript_text:
        return jsonify({"error": "No translated transcript file found"}), 404

    try:
        raw_text = generate_exercises(transcript_text)
        structured = parse_exercise_response(raw_text)

        if structured:
            return jsonify(structured)
        else:
            return jsonify({"error": "Failed to parse exercise response"}), 500
    except Exception as e:
        print("Exercise route error:", str(e))
        return jsonify({"error": "Internal server error"}), 500


transcription_store = {}


def get_available_languages(video_id):
    """Fetch available transcript languages for a YouTube video."""
    try:
        transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
        return [t.language_code for t in transcript_list]
    except TranscriptsDisabled:
        return []
    except Exception:
        return []


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


def extract_transcript(youtube_video_url):
    """Fetch transcript in the original language."""
    try:
        if "=" in youtube_video_url:
            video_id = youtube_video_url.split("=")[1]
        else:
            # Handle youtu.be format or other formats
            video_id = youtube_video_url.split("/")[-1]

        available_languages = get_available_languages(video_id)

        if not available_languages:
            return None, None

        transcript_text = YouTubeTranscriptApi.get_transcript(video_id, languages=[available_languages[0]])
        return " ".join([i["text"] for i in transcript_text]), available_languages[0]
    except NoTranscriptFound:
        return None, None
    except Exception as e:
        return None, str(e)


@app.route('/api/transcribelink', methods=['POST'])
def transcribe_link():
    # Get data from form
    youtube_link = request.form.get('youtube_link')
    target_language = request.form.get('target_language', 'en')

    if not youtube_link:
        return jsonify({"error": "YouTube link is required"}), 400

    try:
        # Extract transcript
        transcript_text, original_language = extract_transcript(youtube_link)

        if transcript_text is None:
            return jsonify({"error": "Could not retrieve transcript for this video in any language"}), 404

        # Transcribe to target language if different
        translated_transcript = transcript_text
        if original_language != target_language:
            translated_transcript = transcribe_to_target_language(transcript_text, target_language)

        # Generate detailed notes
        detailed_notes = generate_detailed_notes(translated_transcript, target_language)

        # Generate unique ID for this transcription set
        transcription_id = str(uuid.uuid4())

        # Store the generated content
        transcription_store[transcription_id] = {
            "original_transcript": transcript_text,
            "original_language": original_language,
            "translated_transcript": translated_transcript,
            "target_language": target_language,
            "detailed_notes": detailed_notes
        }
        with open("transcript.txt", "w", encoding="utf-8") as f:
            f.write(transcript_text)

        # Save translated transcript
        with open("translated_transcript.txt", "w", encoding="utf-8") as f:
            f.write(translated_transcript)

        # Return the response
        return jsonify({
            "success": True,
            "transcription_id": transcription_id,
            "original_language": original_language,
            "target_language": target_language,
            "original_transcript": transcript_text,
            "translated_transcript": translated_transcript,
            "detailed_notes": detailed_notes,
            "download_links": {
                "original_transcript": f"/download/{transcription_id}/original",
                "translated_transcript": f"/download/{transcription_id}/translated",
                "detailed_notes": f"/download/{transcription_id}/notes"
            }
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/download/<transcription_id>/<file_type>', methods=['GET'])
def download_file(transcription_id, file_type):
    if transcription_id not in transcription_store:
        return jsonify({"error": "Transcription not found"}), 404

    transcription_data = transcription_store[transcription_id]

    try:
        # Create a temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.txt', mode='w', encoding='utf-8') as tmp:
            if file_type == 'original':
                tmp.write(transcription_data["original_transcript"])
                filename = f"original_transcript_{transcription_data['original_language']}.txt"
            elif file_type == 'translated':
                tmp.write(transcription_data["translated_transcript"])
                filename = f"translated_transcript_{transcription_data['target_language']}.txt"
            elif file_type == 'notes':
                tmp.write(transcription_data["detailed_notes"])
                filename = f"detailed_notes_{transcription_data['target_language']}.txt"
            else:
                return jsonify({"error": "Invalid file type"}), 400

            tmp_path = tmp.name

        # Send the file
        return send_file(tmp_path, as_attachment=True, download_name=filename)

    except Exception as e:
        return jsonify({"error": str(e)}), 500


def extract_text_from_pdf(file_path):
    """Extract text from a PDF file."""
    with open(file_path, 'rb') as file:
        pdf_reader = PyPDF2.PdfReader(file)
        text = "\n".join([page.extract_text() for page in pdf_reader.pages if page.extract_text()])
    return text


def extract_text_from_docx(file_path):
    """Extract text from a Word (.docx) file."""
    doc = docx.Document(file_path)
    text = "\n".join([para.text for para in doc.paragraphs])
    return text


def translate_notes(notes_text, target_language):
    """Use Google Gemini AI to translate notes into the target language."""
    model = genai.GenerativeModel("gemini-2.0-flash")
    response = model.generate_content(f"Translate the following text into {target_language}:\n\n{notes_text}")
    return response.text if response else notes_text


def save_text_to_file(text, filename):
    """Save text to a file."""
    with open(filename, "w", encoding="utf-8") as file:
        file.write(text)


@app.route("/api/generate-note", methods=["POST"])
def generate_note():
    if 'file' not in request.files:
        return jsonify({"error": "Missing file"}), 400

    file = request.files['file']
    target_language = request.form.get('target_language', 'en')
    filename = file.filename

    if not filename.lower().endswith(('.pdf', '.docx')):
        return jsonify({"error": "Unsupported file format"}), 400

    # Save uploaded file to temp location
    with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(filename)[-1]) as temp_file:
        file.save(temp_file.name)
        temp_path = temp_file.name

    try:
        # Extract text
        if filename.lower().endswith(".pdf"):
            notes_text = extract_text_from_pdf(temp_path)
        else:
            notes_text = extract_text_from_docx(temp_path)

        if not notes_text.strip():
            return jsonify({"error": "No text extracted from the file"}), 400

        # Translate notes
        translated_notes = translate_notes(notes_text, target_language)

        # Save to file
        save_text_to_file(translated_notes, "translated_notes.txt")

        return jsonify({
            "original_notes": notes_text,
            "translated_notes": translated_notes,
            "message": "Notes translated and saved to translated_notes.txt"
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        os.unlink(temp_path)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5003)
