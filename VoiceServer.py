import os
import uuid
import logging
import torch
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from werkzeug.utils import secure_filename
from faster_whisper import WhisperModel
from deep_translator import GoogleTranslator

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Configuration
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'mp3', 'wav'}

# Ensure upload directory exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


class AudioTranscriber:
    def __init__(self, model_size="large-v3", device=None, compute_type="float16"):
        """Initialize speech-to-text transcriber."""
        self.device = device if device else ("cuda" if torch.cuda.is_available() else "cpu")
        self.compute_type = "float16" if self.device == "cuda" else "int8"

        print(f"🔹 Using device: {self.device.upper()} ({'GPU' if self.device == 'cuda' else 'CPU'})")

        # Load Whisper model
        self.model = WhisperModel(model_size, device=self.device, compute_type=self.compute_type)

    def transcribe_audio(self, audio_path, input_language='en', output_language='en'):
        """
        Transcribe and optionally translate audio file.

        Args:
            audio_path (str): Path to the audio file
            input_language (str): Language of the input audio
            output_language (str): Desired output language

        Returns:
            dict: Transcription and translation results
        """
        try:
            # Transcribe audio
            segments, info = self.model.transcribe(
                audio_path, beam_size=5, language=input_language, vad_filter=True)

            # Collect transcription segments
            transcription_segments = []
            full_transcription = ""
            for segment in segments:
                text = segment.text.strip()
                transcription_segments.append({
                    'start': segment.start,
                    'end': segment.end,
                    'text': text
                })
                full_transcription += text + " "

            # Translate if languages differ
            translated_text = full_transcription
            if output_language and output_language != input_language:
                try:
                    translator = GoogleTranslator(source=input_language, target=output_language)
                    translated_text = translator.translate(full_transcription)
                except Exception as e:
                    print(f"⚠️ Translation error: {e}")

            return {
                'input_language': input_language,
                'output_language': output_language,
                'transcription': full_transcription.strip(),
                'translated_text': translated_text.strip(),
                'segments': transcription_segments
            }

        except Exception as e:
            print(f"❌ Transcription error: {e}")
            return {'error': str(e)}


# Initialize transcriber
transcriber = AudioTranscriber()


def allowed_file(filename):
    """Check if file extension is allowed."""
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/')
def index():
    """Render the main page."""
    return render_template('voicefrontend.html')


@app.route('/api/voice', methods=['POST'])
def transcribe_audio():
    """
    Endpoint to handle audio file transcription.

    Expects:
    - audio file in multipart/form-data
    - Optional form fields: input_language, output_language
    """
    # Check if file is present
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400

    file = request.files['file']

    # Check if filename is empty
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    # Check file type
    if not allowed_file(file.filename):
        return jsonify({'error': 'Invalid file type. Only MP3 and WAV allowed'}), 400

    # Get optional language parameters
    input_language = request.form.get('input_language', 'en')
    output_language = request.form.get('output_language', 'en')

    try:
        # Generate unique filename
        filename = f"{uuid.uuid4()}_{secure_filename(file.filename)}"
        filepath = os.path.join(UPLOAD_FOLDER, filename)

        # Save file
        file.save(filepath)

        try:
            # Transcribe audio
            result = transcriber.transcribe_audio(
                filepath,
                input_language=input_language,
                output_language=output_language
            )

            # Clean up file after processing
            os.remove(filepath)

            return jsonify(result)

        except Exception as e:
            # Ensure file is deleted even if transcription fails
            if os.path.exists(filepath):
                os.remove(filepath)
            return jsonify({'error': str(e)}), 500

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/health', methods=['GET'])
def health_check():
    """Simple health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'device': transcriber.device,
        'model': 'Whisper Large v3'
    })


if __name__ == '__main__':
    # Configure logging
    logging.basicConfig(level=logging.INFO)

    # Run Flask app
    app.run(host='0.0.0.0', port=5008, debug=True)