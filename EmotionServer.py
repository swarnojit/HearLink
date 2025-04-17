import json
from PIL import Image
from flask import Flask, request, jsonify, send_file
import cv2
import uuid
from deepface import DeepFace
from collections import Counter
import matplotlib.pyplot as plt
from datetime import datetime
import os
import google.generativeai as genai
from flask_cors import CORS
app = Flask(__name__)
CORS(app)
# Create directories if they don't exist
UPLOAD_FOLDER = 'uploads'
RESULTS_FOLDER = 'results'
for folder in [UPLOAD_FOLDER, RESULTS_FOLDER]:
    os.makedirs(folder, exist_ok=True)
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Load face cascade classifier
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')


@app.route('/api/test', methods=['GET'])
def test():
    return jsonify({'result': 'ok'})


@app.route('/api/analyze-emotion', methods=['POST'])
def analyze_emotion():
    if 'video' not in request.files:
        return jsonify({'error': 'No video file provided'}), 400

    video_file = request.files['video']
    if video_file.filename == '':
        return jsonify({'error': 'No video selected'}), 400

    # Save the uploaded video to a temporary file
    temp_video_path = os.path.join(UPLOAD_FOLDER, f"{uuid.uuid4()}.mp4")
    video_file.save(temp_video_path)

    try:
        # Process the video
        result = process_video(temp_video_path)

        # Return the results
        return jsonify({
            'report_path': "/download-report",
            'chart_path': "/download-chart",
            'report_file_path': os.path.join(RESULTS_FOLDER, "emotion_report.txt"),
            'chart_file_path': os.path.join(RESULTS_FOLDER, "chart.png"),
            'top_emotion': result['top_emotion'],
            'second_emotion': result['second_emotion'],
            'distress_percentage': result['distress_percentage'],
            'alert_triggered': result['alert_triggered']
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        # Clean up the temporary video file
        if os.path.exists(temp_video_path):
            os.remove(temp_video_path)


@app.route('/api/download-chart', methods=['GET'])
def download_chart():
    return send_file(os.path.join(RESULTS_FOLDER, "chart.png"), as_attachment=True)


@app.route('/api/download-report', methods=['GET'])
def download_report():
    return send_file(os.path.join(RESULTS_FOLDER, "emotion_report.txt"), as_attachment=True)


def process_video(video_path):
    """Process video file and analyze emotions."""
    # Open the video file
    cap = cv2.VideoCapture(video_path)

    if not cap.isOpened():
        raise Exception("Error: Could not open video file.")

    # Emotion tracking variables
    emotion_counts = Counter()
    total_frames = 0
    alert_emotions = ["sad", "angry", "fear"]
    distress_threshold = 15  # 15% threshold for distress alert

    # Set frame skip rate (process every n frames)
    # For a 10-minute video at 30fps, processing every 30 frames = 1 frame per second
    frame_skip = 30

    frame_count = 0
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # Process only every n frames
        if frame_count % frame_skip == 0:
            # Convert frame to grayscale
            gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            rgb_frame = cv2.cvtColor(gray_frame, cv2.COLOR_GRAY2RGB)

            # Detect faces
            faces = face_cascade.detectMultiScale(gray_frame, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

            emotions_detected = []
            for (x, y, w, h) in faces:
                face_roi = rgb_frame[y:y + h, x:x + w]

                # Perform emotion analysis
                try:
                    result = DeepFace.analyze(face_roi, actions=['emotion'], enforce_detection=False)
                    # Get the dominant emotion
                    emotion = result[0]['dominant_emotion']
                    emotions_detected.append(emotion)
                except Exception as e:
                    print(f"Error analyzing face: {e}")

            # Update emotion counters
            emotion_counts.update(emotions_detected)
            total_frames += 1

        frame_count += 1

    # Release the video capture object
    cap.release()

    # Generate results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    result_id = f"{timestamp}_{uuid.uuid4().hex[:8]}"

    # Create the pie chart
    chart_filename = "chart.png"
    chart_path = os.path.join(RESULTS_FOLDER, chart_filename)

    # Calculate results
    most_common = emotion_counts.most_common(2)
    top_emotion = most_common[0][0] if len(most_common) > 0 else "None"
    second_top_emotion = most_common[1][0] if len(most_common) > 1 else "None"

    # Calculate distress percentage
    distress_frames = sum(emotion_counts[e] for e in alert_emotions if e in emotion_counts)
    distress_percentage = 0
    if total_frames > 0:
        distress_percentage = (distress_frames / total_frames) * 100

    alert_triggered = distress_percentage >= distress_threshold

    # Generate pie chart exactly as in the original code
    plt.figure(figsize=(6, 6))  # Original size was 6,6
    if total_frames > 0 and emotion_counts:
        labels = emotion_counts.keys()
        sizes = [emotion_counts[e] for e in labels]
        plt.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90, colors=plt.cm.Paired.colors)
        plt.title("Emotion Distribution Over Time")  # Original title
    else:
        plt.text(0.5, 0.5, "No emotions detected", ha='center', va='center', fontsize=12)
        plt.title("No Data Available")

    plt.savefig(chart_path)
    plt.close()

    # Save report to text file - same format as original
    report_filename = "emotion_report.txt"
    report_path = os.path.join(RESULTS_FOLDER, report_filename)

    with open(report_path, "w", encoding="utf-8") as file:
        file.write("🔹 **Emotion Analysis Report** 🔹\n")
        file.write(f"📌 Top Emotion: {top_emotion}\n")
        file.write(f"📌 Second Most Common Emotion: {second_top_emotion}\n")
        file.write(f"⚠ Emotional Distress Percentage: {distress_percentage:.2f}%\n")
        if alert_triggered:
            file.write("🚨 ALERT: Significant emotional distress detected! 🚨\n")

    return {
        'report_filename': report_filename,
        'chart_filename': chart_filename,
        'top_emotion': top_emotion,
        'second_emotion': second_top_emotion,
        'distress_percentage': round(distress_percentage, 2),
        'alert_triggered': alert_triggered
    }


#emotion extraction code
def extract_emotions_from_pie_chart(image_path):
    """Uses Gemini to extract text (emotion percentages) from the pie chart image."""
    model = genai.GenerativeModel("gemini-2.0-flash")

    # Open the image using PIL
    image = Image.open(image_path)

    prompt = """Extract emotion percentages from this pie chart image.
    The emotions include: neutral, happy, sad, angry, fear, and disgust.
    Provide the output in JSON format like this:
    {
        "neutral": 60,
        "happy": 30,
        "sad": 5,
        "angry": 3,
        "fear": 2,
        "disgust": 0
    }
    IMPORTANT: Only respond with the JSON data and nothing else."""

    response = model.generate_content([prompt, image])

    try:
        # Print the raw response to help with debugging
        print("Raw Gemini response:")
        print(response.text)

        # Extract the JSON part from the response
        # First try to parse directly
        try:
            emotion_data = json.loads(response.text)
        except json.JSONDecodeError:
            # If direct parsing fails, try to find and extract JSON content
            import re
            json_match = re.search(r'\{.*\}', response.text, re.DOTALL)
            if json_match:
                json_str = json_match.group(0)
                emotion_data = json.loads(json_str)
            else:
                raise Exception("Could not find valid JSON in the response")

        return Counter(emotion_data)
    except Exception as e:
        print("Error parsing OCR output:", e)
        print("Full response was:", response.text)
        return None


def analyze_emotion_data(emotion_counts):
    """Analyzes emotion data to determine distress levels."""
    total_frames = sum(emotion_counts.values())
    distress_emotions = ["sad", "angry", "fear", "disgust"]

    distress_percentage = sum(emotion_counts.get(e, 0) for e in distress_emotions) / total_frames * 100
    neutral_happy_percentage = (emotion_counts.get("neutral", 0) + emotion_counts.get("happy", 0)) / total_frames * 100

    return distress_percentage, neutral_happy_percentage


def generate_teacher_feedback(distress_percentage):
    """Generates structured teacher feedback using Gemini based on emotional distress levels."""
    if distress_percentage >= 20:
        severity = "High"
        prompt = f"""
        The classroom analysis shows a high emotional distress level of {distress_percentage:.2f}%. 
        Provide structured feedback for the teacher including:
        1. Possible reasons why students may be experiencing distress.
        2. Practical steps the teacher can take to create a more inclusive and engaging environment.
        3. Expected improvement percentage if these steps are implemented.
        """
    elif distress_percentage >= 10:
        severity = "Moderate"
        prompt = f"""
        The classroom analysis shows a moderate emotional distress level of {distress_percentage:.2f}%. 
        Provide structured feedback for the teacher including:
        1. Minor adjustments the teacher can make to improve student engagement.
        2. Potential reasons for discomfort and how to address them.
        3. Expected improvement percentage if these adjustments are made.
        """
    else:
        return "✅ Great job! The class environment is well-balanced with minimal distress. Keep up the excellent work!"

    model = genai.GenerativeModel("gemini-2.0-flash")
    response = model.generate_content(prompt)
    return response.text


@app.route('/api/analyze-pie', methods=['GET'])
def analyze_pie():
    """Analyze the pie chart and return emotion analysis results"""
    chart_path = os.path.join(RESULTS_FOLDER, "chart.png")

    # Check if chart exists
    if not os.path.exists(chart_path):
        return jsonify({"error": "No chart available. Please run /analyze-emotion first."}), 400

    try:
        # Extract emotion data from the pie chart
        emotion_counts = extract_emotions_from_pie_chart(chart_path)
        if not emotion_counts:
            return jsonify({"error": "Error extracting emotions from pie chart."}), 500

        # Analyze extracted emotion data
        distress_percentage, neutral_happy_percentage = analyze_emotion_data(emotion_counts)

        # Generate feedback for teachers
        feedback = generate_teacher_feedback(distress_percentage)

        # Save feedback to file
        feedback_path = os.path.join(RESULTS_FOLDER, "teacher_feedback.txt")
        with open(feedback_path, "w", encoding="utf-8") as file:
            file.write(feedback)

        # Return JSON response with analysis results
        return jsonify({
            "emotion_counts": dict(emotion_counts),
            "distress_percentage": distress_percentage,
            "neutral_happy_percentage": neutral_happy_percentage,
            "feedback": feedback,
            "feedback_download_url": "/api/download/feedback"
        }), 200

    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500


@app.route('/api/download/feedback', methods=['GET'])
def download_feedback():
    """Download the teacher feedback as a text file"""
    feedback_path = os.path.join(RESULTS_FOLDER, "teacher_feedback.txt")

    # Check if feedback file exists
    if not os.path.exists(feedback_path):
        return jsonify({"error": "No feedback available. Please run /analyze-pie first."}), 400

    try:
        return send_file(
            feedback_path,
            as_attachment=True,
            download_name="teacher_feedback.txt",
            mimetype="text/plain"
        )
    except Exception as e:
        return jsonify({"error": f"Error downloading feedback: {str(e)}"}), 500


@app.route('/api/upload-chart', methods=['POST'])
def upload_chart():
    """Upload a pie chart image for analysis"""
    if 'chart' not in request.files:
        return jsonify({"error": "No file part in the request"}), 400

    file = request.files['chart']

    if file.filename == '':
        return jsonify({"error": "No file selected"}), 400

    try:
        # Save the uploaded chart
        file_path = os.path.join(RESULTS_FOLDER, "chart.png")
        file.save(file_path)

        return jsonify({
            "message": "Chart uploaded successfully",
            "next_step": "Run /api/analyze-pie to analyze the chart"
        }), 200

    except Exception as e:
        return jsonify({"error": f"Error uploading chart: {str(e)}"}), 500


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5006)
