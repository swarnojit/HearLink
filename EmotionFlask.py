import cv2
from flask import Flask, render_template, Response, jsonify
from deepface import DeepFace
import numpy as np
import threading
import queue

app = Flask(__name__)

# Initialize video capture
cap = cv2.VideoCapture(0)
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

# Shared queues
frame_queue = queue.Queue(maxsize=1)
emotion_queue = queue.Queue(maxsize=1)

# Track emotion counts
emotion_counts = {"happy": 0, "sad": 0, "angry": 0, "surprise": 0, "neutral": 0}


def process_frame(frame):
    """Detect faces and analyze emotions in a frame."""
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

    output_frame = frame.copy()
    current_emotion = "Neutral"

    for (x, y, w, h) in faces:
        face_roi = frame[y:y + h, x:x + w]

        try:
            result = DeepFace.analyze(face_roi, actions=['emotion'], enforce_detection=False)
            current_emotion = result[0]['dominant_emotion']

            # Update emotion counts
            if current_emotion in emotion_counts:
                emotion_counts[current_emotion] += 1

            cv2.rectangle(output_frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            cv2.putText(output_frame, f"{current_emotion}", (x, y - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.9, (36, 255, 12), 2)
        except Exception as e:
            print(f"Emotion detection error: {e}")

    return output_frame, current_emotion


def capture_frames():
    """Continuously capture and process frames."""
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        processed_frame, current_emotion = process_frame(frame)

        # Update frame queue
        if not frame_queue.full():
            frame_queue.put(processed_frame)

        # Update emotion queue
        if not emotion_queue.full():
            emotion_queue.put(current_emotion)


def generate_frames():
    """Generate frames as an MJPEG stream."""
    while True:
        frame = frame_queue.get()
        ret, buffer = cv2.imencode('.jpg', frame)
        if not ret:
            continue

        # Yield in MJPEG format
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/video_feed')
def video_feed():
    """Returns video stream as MJPEG."""
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/emotion_data')
def get_emotion_data():
    """Returns the latest detected emotion."""
    try:
        current_emotion = emotion_queue.get(block=False)
    except queue.Empty:
        current_emotion = "Neutral"

    return jsonify({
        "current_emotion": current_emotion,
        "emotion_counts": emotion_counts
    })


if __name__ == '__main__':
    capture_thread = threading.Thread(target=capture_frames, daemon=True)
    capture_thread.start()

    app.run(debug=True, host='0.0.0.0')
