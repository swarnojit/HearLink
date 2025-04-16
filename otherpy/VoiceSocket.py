import os
import tempfile
import imageio_ffmpeg as ffmpeg  # Use this instead of "import ffmpeg"

import io
import logging
import torch
import base64
import threading
import queue
from flask import Flask, render_template
from flask_cors import CORS
from flask_socketio import SocketIO, emit
from faster_whisper import WhisperModel
from deep_translator import GoogleTranslator

# Flask Setup
app = Flask(__name__)
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*", ping_timeout=60, ping_interval=25)

# Speech Recognition Class
class RealTimeTranscriber:
    def __init__(self, model_size="large-v3", input_language="en", output_language="en"):
        """Initialize real-time transcriber."""
        print(f"[DEBUG] Initializing Transcriber: Input={input_language}, Output={output_language}")
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.compute_type = "float16" if self.device == "cuda" else "int8"
        print(f"[DEBUG] Using Device: {self.device.upper()}")

        # Load Whisper Model
        self.model = WhisperModel(model_size, device=self.device, compute_type=self.compute_type)

        # Queue for audio chunks
        self.data_queue = queue.Queue()
        self.is_listening = True
        self.transcription_thread = threading.Thread(target=self.transcription_worker, daemon=True)
        self.transcription_thread.start()

    def transcription_worker(self):
        """Background worker to process audio queue."""
        print("[DEBUG] Transcription Worker Started")
        while self.is_listening:
            try:
                audio_data = self.data_queue.get(timeout=1)
                if audio_data == "STOP":
                    print("[DEBUG] Stopping transcription worker")
                    break

                print("[DEBUG] Transcribing audio...")
                segments, _ = self.model.transcribe(audio_data, beam_size=5, language="en", vad_filter=True)

                for segment in segments:
                    text = segment.text.strip()
                    translated_text = self.translate_text(text)

                    # Emit Transcription
                    socketio.emit("transcription_update", {
                        "original_text": text,
                        "translated_text": translated_text
                    })
            except queue.Empty:
                continue
            except Exception as e:
                print(f"[DEBUG] Transcription Error: {e}")

    def translate_text(self, text):
        """Translate text."""
        try:
            translator = GoogleTranslator(source="en", target="en")  # Change if needed
            return translator.translate(text)
        except Exception as e:
            print(f"[DEBUG] Translation Error: {e}")
            return text

    def process_audio_chunk(self, audio_chunk):
        """Process received audio chunks."""
        self.data_queue.put(audio_chunk)

    def stop(self):
        """Stop Transcription Worker."""
        self.is_listening = False
        self.data_queue.put("STOP")


# Global Transcriber Instance
transcriber = None


@app.route("/")
def index():
    """Serve HTML UI."""
    return render_template("socket.html")


@socketio.on("connect")
def handle_connect():
    """Handle new WebSocket connection."""
    print("[DEBUG] Client Connected")
    emit("connection_status", {"status": "connected"})


@socketio.on("start_transcription")
def handle_start_transcription():
    global transcriber
    if transcriber is None:
        print("[DEBUG] Creating new transcriber instance ✅")
        transcriber = RealTimeTranscriber()
    else:
        print("[DEBUG] Transcriber already running 🚀")


@socketio.on("audio_chunk")
def handle_audio_chunk(data):
    global transcriber
    if transcriber is None:
        print("[ERROR] No active transcriber! Ignoring audio chunk 🚨")
        return

    try:
        # Decode base64 audio
        if "," in data["audio"]:
            data["audio"] = data["audio"].split(",")[1]
        audio_bytes = base64.b64decode(data["audio"])
        print(f"[DEBUG] Received audio chunk of {len(audio_bytes)} bytes ✅")

        # Save WebM audio to temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".webm") as temp_input:
            temp_input.write(audio_bytes)
            temp_input_path = temp_input.name

        # Convert WebM to WAV
        temp_wav_path = temp_input_path.replace(".webm", ".wav")
        ffmpeg.input(temp_input_path).output(temp_wav_path, format="wav").run(overwrite_output=True)

        # Transcribe WAV file
        transcriber.process_audio_chunk(temp_wav_path)

        # Cleanup
        os.remove(temp_input_path)  # Remove WebM file
        os.remove(temp_wav_path)  # Remove WAV file after processing

    except Exception as e:
        print(f"[ERROR] Transcription Error: {e}")


@socketio.on("stop_transcription")
def handle_stop_transcription():
    global transcriber
    if transcriber is None:
        print("[DEBUG] No Transcriber Running, Ignoring Stop Request ❌")
        return
    print("[DEBUG] Stopping Transcription... ✅")
    transcriber.stop()
    transcriber = None  # Reset after stopping



if __name__ == "__main__":
    socketio.run(app, debug=True, allow_unsafe_werkzeug=True)
