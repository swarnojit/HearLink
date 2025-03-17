import threading
import queue
import io
import logging
import pyaudio
import speech_recognition as sr
import time
import torch  # For checking CUDA availability
from faster_whisper import WhisperModel
from deep_translator import GoogleTranslator

class STT:
    def __init__(self, model_size="large-v3", device=None, compute_type="float16",
                 input_language="en", output_language="en", logging_level=None):
        """Initialize real-time speech-to-text with translation."""
        self.recorder = sr.Recognizer()
        self.data_queue = queue.Queue()
        self.transcription = ['']
        self.last_transcription = ""
        self.is_listening = True

        self.model_size = model_size
        self.device = device if device else ("cuda" if torch.cuda.is_available() else "cpu")  # Auto-detect GPU/CPU
        self.compute_type = "float16" if self.device == "cuda" else "int8"  # Use int8 for CPU to save memory
        self.input_language = input_language
        self.output_language = output_language
        self.default_mic = self.setup_mic()

        print(f"🔹 Using device: {self.device.upper()} ({'GPU' if self.device == 'cuda' else 'CPU'})")

        # Load Whisper model
        self.model = WhisperModel(self.model_size, device=self.device, compute_type=self.compute_type)
        self.lock = threading.Lock()

        if logging_level:
            self.configure_logging(level=logging_level)

        # ✅ Ensure the transcription thread always starts
        self.thread = threading.Thread(target=self.transcribe)
        self.thread.daemon = True  # ✅ Fix: Use daemon attribute instead of setDaemon()
        self.thread.start()

        logging.info("✅ Ready!")
        print("✅ Ready!")

    def transcribe(self):
        """Process audio from queue and transcribe it."""
        while self.is_listening:
            audio_data = self.data_queue.get()
            if audio_data == 'STOP':
                break
            
            segments, info = self.model.transcribe(
                audio_data, beam_size=5, language=self.input_language, vad_filter=True)
            
            for segment in segments:
                text = segment.text.strip()
                logging.info(f"[{segment.start:.2f}s -> {segment.end:.2f}s] {text}")
                with self.lock:
                    self.transcription.append(text)
                    self.last_transcription = text
                
                if self.output_language and self.output_language != self.input_language:
                    translated_text = self.translate_text(text)
                    print(f"🔄 Translated: {translated_text}")

            self.data_queue.task_done()
            time.sleep(0.25)

    def translate_text(self, text):
        """Translate text from input language to output language."""
        try:
            translator = GoogleTranslator(source=self.input_language, target=self.output_language)
            return translator.translate(text)
        except Exception as e:
            print(f"⚠️ Translation error: {e}")
            return text

    def recorder_callback(self, _, audio_data):
        """Callback function to receive live audio."""
        audio = io.BytesIO(audio_data.get_wav_data())
        self.data_queue.put(audio)

    def listen(self):
        """Start microphone and begin listening."""
        with sr.Microphone(device_index=self.default_mic) as source:
            print("🎤 Adjusting for ambient noise... Please wait.")
            self.recorder.adjust_for_ambient_noise(source, duration=1)  # Adjust for background noise

        # ✅ Start listening properly
        self.listener = self.recorder.listen_in_background(source, self.recorder_callback)
        print("🎧 Listening... Speak now!")

    def stop(self):
        """Stop transcription process."""
        logging.info("🛑 Stopping...")
        logging.info(f"📝 Final Transcription:\n {self.transcription}")
        self.is_listening = False
        self.data_queue.put("STOP")

    def get_last_transcription(self):
        """Retrieve last recorded transcription."""
        with self.lock:
            text = self.last_transcription
            self.last_transcription = ""
        return text

    @staticmethod
    def setup_mic():
        """Detect and set up the default microphone."""
        p = pyaudio.PyAudio()
        default_device_index = None
        try:
            default_input = p.get_default_input_device_info()
            default_device_index = default_input["index"]
        except (IOError, OSError):
            logging.error("⚠️ Default input device not found. Listing all available input devices:")
            for i in range(p.get_device_count()):
                info = p.get_device_info_by_index(i)
                if info['maxInputChannels'] > 0:
                    logging.info(f"🎙️ Device index: {i}, Device name: {info['name']}")
                    if default_device_index is None:
                        default_device_index = i
        if default_device_index is None:
            raise Exception("❌ No input devices found. Please check your microphone.")
        return default_device_index

    @staticmethod
    def configure_logging(level="INFO"):
        """Set up logging configuration."""
        levels = {
            'DEBUG': logging.DEBUG,
            'INFO': logging.INFO,
            'WARNING': logging.WARNING,
            'ERROR': logging.ERROR,
            'CRITICAL': logging.CRITICAL
        }
        logging.basicConfig(level=levels.get(level.upper(), logging.INFO))

# 🚀 **Usage Example**
try:
    input_lang = input("🌍 Enter input language (e.g., 'en', 'hi', 'ta', 'bn'): ")
    output_lang = input("🌍 Enter output language (e.g., 'en', 'hi', 'ta', 'bn'): ")

    stt = STT(input_language=input_lang, output_language=output_lang)
    stt.listen()
    
    while stt.is_listening:
        last_transcription = stt.get_last_transcription()
        if last_transcription:
            print(f"🎤 You said ({input_lang}):", last_transcription)
            if output_lang != input_lang:
                translated_text = stt.translate_text(last_transcription)
                print(f"📝 Translated ({output_lang}):", translated_text)
            if "stop" in last_transcription.lower():
                stt.stop()
        time.sleep(1)

except KeyboardInterrupt:
    pass


