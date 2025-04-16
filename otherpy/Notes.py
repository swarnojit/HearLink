from flask import Flask, request, jsonify, send_file
from werkzeug.utils import secure_filename
import os
import google.generativeai as genai
from dotenv import load_dotenv
import PyPDF2
import docx
import tempfile
import uuid
import io

# Load environment variables from .env file
load_dotenv()
# Configure Google Gemini AI with API key
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

app = Flask(__name__)

# Configure upload settings
UPLOAD_FOLDER = tempfile.gettempdir()  # Use system temp directory
ALLOWED_EXTENSIONS = {'pdf', 'docx'}  # Only allow these file types
TRANSLATION_CACHE = {}  # In-memory cache to store translations

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size


def allowed_file(filename):
    """Check if the uploaded file has an allowed extension."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def extract_text_from_pdf(file_path):
    """Extract text content from a PDF file."""
    with open(file_path, 'rb') as file:
        pdf_reader = PyPDF2.PdfReader(file)
        text = "\n".join([page.extract_text() for page in pdf_reader.pages if page.extract_text()])
    return text


def extract_text_from_docx(file_path):
    """Extract text content from a Word (.docx) file."""
    doc = docx.Document(file_path)
    text = "\n".join([para.text for para in doc.paragraphs])
    return text


def translate_notes(notes_text, target_language):
    """Translate text using Google Gemini AI."""
    model = genai.GenerativeModel("gemini-2.0-flash")
    response = model.generate_content(f"Translate the following text into {target_language}:\n\n{notes_text}")
    return response.text if response else notes_text


@app.route('/api/notes', methods=['POST'])
def translate_document():
    """
    Main endpoint to translate documents

    Accepts:
    - POST request with multipart/form-data
    - 'file': PDF or DOCX file
    - 'target_language': Language code (e.g., 'en', 'hi', 'fr')

    Returns:
    - JSON with original text, translated text, and download link
    """
    # Check if a file was included in the request
    if 'file' not in request.files:
        return jsonify({'error': 'No file part in the request'}), 400

    file = request.files['file']

    # Check if file is empty
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400

    # Check if file type is allowed
    if not allowed_file(file.filename):
        return jsonify({'error': f'File type not allowed. Please upload {", ".join(ALLOWED_EXTENSIONS)}'}), 400

    # Get target language (default to English if not specified)
    target_language = request.form.get('target_language', 'en')

    # Save the file temporarily for processing
    filename = secure_filename(file.filename)
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(file_path)

    try:
        # Extract text based on file type
        file_extension = filename.rsplit('.', 1)[1].lower()

        if file_extension == 'pdf':
            notes_text = extract_text_from_pdf(file_path)
        elif file_extension == 'docx':
            notes_text = extract_text_from_docx(file_path)
        else:
            return jsonify({'error': 'Unsupported file type'}), 400

        # Check if text was extracted successfully
        if not notes_text:
            return jsonify({'error': 'Could not extract text from the file'}), 400

        # Translate the text
        translated_text = translate_notes(notes_text, target_language)

        # Generate a unique ID for this translation
        translation_id = str(uuid.uuid4())

        # Store the translation in our cache
        TRANSLATION_CACHE[translation_id] = {
            'original_text': notes_text,
            'translated_text': translated_text,
            'target_language': target_language,
            'original_filename': os.path.splitext(filename)[0]
        }

        # Return the results with download link
        return jsonify({
            'translation_id': translation_id,
            'original_text': notes_text,
            'translated_text': translated_text,
            'target_language': target_language,
            'download_url': f'/api/download/{translation_id}'
        }), 200

    except Exception as e:
        return jsonify({'error': f'An error occurred: {str(e)}'}), 500

    finally:
        # Clean up the temporary file
        if os.path.exists(file_path):
            os.remove(file_path)


@app.route('/api/download/<translation_id>', methods=['GET'])
def download_translation(translation_id):
    """
    Endpoint to download a translated document

    Accepts:
    - GET request with translation_id in URL path

    Returns:
    - Text file download with the translated content
    """
    # Check if the translation exists in our cache
    if translation_id not in TRANSLATION_CACHE:
        return jsonify({'error': 'Translation not found or expired'}), 404

    translation_data = TRANSLATION_CACHE[translation_id]
    translated_text = translation_data['translated_text']
    original_filename = translation_data['original_filename']
    target_language = translation_data['target_language']

    # Create a file-like object in memory
    text_io = io.StringIO(translated_text)
    bytes_io = io.BytesIO(text_io.getvalue().encode('utf-8'))

    # Create the filename for the download
    download_filename = f"{original_filename}_{target_language}_translation.txt"

    # Return the file for download
    return send_file(
        bytes_io,
        as_attachment=True,
        download_name=download_filename,
        mimetype='text/plain'
    )


@app.route('/api/health', methods=['GET'])
def health_check():
    """
    Health check endpoint

    Used to verify API is running and responsive
    """
    return jsonify({'status': 'healthy'}), 200


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)