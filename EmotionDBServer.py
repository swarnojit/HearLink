import io
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
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_user, LoginManager
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
CORS(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///emotions.db'
app.config['SECRET_KEY'] = 'fdsfasdfsad34234sdfsd'

# Initialize extensions
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)

# Create directories if they don't exist
UPLOAD_FOLDER = 'uploads'
RESULTS_FOLDER = 'results'
for folder in [UPLOAD_FOLDER, RESULTS_FOLDER]:
    os.makedirs(folder, exist_ok=True)
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Load face cascade classifier
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)


class EmotionAnalysis(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('user.id'), unique=True, nullable=False)
    top_emotion = db.Column(db.String(50))
    second_emotion = db.Column(db.String(50))
    distress_percentage = db.Column(db.Float)
    alert_triggered = db.Column(db.Boolean)
    chart_image = db.Column(db.LargeBinary)
    pie_chart_analysis = db.Column(db.String(1000))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    student = db.relationship('User', backref=db.backref('analysis', uselist=False))


@app.route('/api/test', methods=['GET'])
def test():
    return jsonify({'result': 'ok'})


@app.route('/api/register', methods=['POST'])
def register():
    data = request.get_json()

    # Validate input
    if not data or not data.get('username') or not data.get('password'):
        return jsonify({'error': 'Missing username or password'}), 400

    username = data.get('username')
    password = data.get('password')

    # Check if the username already exists
    existing_user = User.query.filter_by(username=username).first()
    if existing_user:
        return jsonify({'error': 'Username already exists'}), 400

    # Create a new user
    hashed_password = generate_password_hash(password)
    new_user = User(username=username, password=hashed_password)

    db.session.add(new_user)
    db.session.commit()

    return jsonify({'message': 'User registered successfully'}), 201


@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()

    # Validate input
    if not data or not data.get('username') or not data.get('password'):
        return jsonify({'error': 'Missing username or password'}), 400

    username = data.get('username')
    password = data.get('password')

    # Find the user by username
    user = User.query.filter_by(username=username).first()
    if not user or not check_password_hash(user.password, password):
        return jsonify({'error': 'Invalid username or password'}), 401

    # Login the user
    login_user(user)

    return jsonify({'message': 'Login successful', 'student_id': user.id}), 200


@app.route('/api/analyze-emotion', methods=['POST'])
def analyze_emotion():
    if 'video' not in request.files or 'student_id' not in request.form:
        return jsonify({'error': 'Missing video file or student ID'}), 400

    video_file = request.files['video']
    student_id = request.form['student_id']

    if video_file.filename == '':
        return jsonify({'error': 'No video selected'}), 400

    # Save video temporarily
    temp_video_path = os.path.join(UPLOAD_FOLDER, f"{uuid.uuid4()}.mp4")
    video_file.save(temp_video_path)

    try:
        # Process and save analysis to DB
        result = process_video(temp_video_path, student_id)

        return jsonify({
            'top_emotion': result['top_emotion'],
            'second_emotion': result['second_emotion'],
            'distress_percentage': result['distress_percentage'],
            'alert_triggered': result['alert_triggered']
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        if os.path.exists(temp_video_path):
            os.remove(temp_video_path)


@app.route('/api/students/all', methods=['GET'])
def get_all_students():
    """Get all students' details along with their emotion analysis data"""
    try:
        # Query all students with their analysis data using the relationship
        students = User.query.all()

        students_data = []
        for student in students:
            # Get the emotion analysis data for this student
            analysis = student.analysis  # This uses the backref from the relationship

            student_info = {
                'id': student.id,
                'username': student.username,
                'analysis': None
            }

            if analysis:
                # Convert binary chart image to base64 for frontend display
                chart_base64 = None
                if analysis.chart_image:
                    import base64
                    chart_base64 = base64.b64encode(analysis.chart_image).decode('utf-8')

                student_info['analysis'] = {
                    'top_emotion': analysis.top_emotion,
                    'second_emotion': analysis.second_emotion,
                    'distress_percentage': analysis.distress_percentage,
                    'alert_triggered': analysis.alert_triggered,
                    'chart_image_base64': chart_base64,  # Base64 encoded image
                    'timestamp': analysis.timestamp.isoformat() if analysis.timestamp else None
                }

            students_data.append(student_info)

        return jsonify({
            'students': students_data,
            'total_count': len(students_data),
            'timestamp': datetime.utcnow().isoformat()
        }), 200

    except Exception as e:
        return jsonify({'error': f'Failed to fetch students data: {str(e)}'}), 500


@app.route('/api/download-chart', methods=['GET'])
def download_chart():
    return send_file(os.path.join(RESULTS_FOLDER, "chart.png"), as_attachment=True)


@app.route('/api/download-report', methods=['GET'])
def download_report():
    return send_file(os.path.join(RESULTS_FOLDER, "emotion_report.txt"), as_attachment=True)


def process_video(video_path, student_id):
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise Exception("Error: Could not open video file.")

    emotion_counts = Counter()
    total_frames = 0
    alert_emotions = ["sad", "angry", "fear"]
    distress_threshold = 15
    frame_skip = 30
    frame_count = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        if frame_count % frame_skip == 0:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            rgb = cv2.cvtColor(gray, cv2.COLOR_GRAY2RGB)
            faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

            for (x, y, w, h) in faces:
                roi = rgb[y:y + h, x:x + w]
                try:
                    result = DeepFace.analyze(roi, actions=['emotion'], enforce_detection=False)
                    emotion = result[0]['dominant_emotion']
                    emotion_counts[emotion] += 1
                except Exception as e:
                    print(f"Emotion detection error: {e}")

            total_frames += 1
        frame_count += 1

    cap.release()

    # Results
    top_emotion = emotion_counts.most_common(1)[0][0] if emotion_counts else "None"
    second_emotion = emotion_counts.most_common(2)[1][0] if len(emotion_counts) > 1 else "None"

    distress_frames = sum(emotion_counts[e] for e in alert_emotions if e in emotion_counts)
    distress_percentage = (distress_frames / total_frames) * 100 if total_frames > 0 else 0
    alert_triggered = distress_percentage >= distress_threshold

    # Generate pie chart
    chart_stream = io.BytesIO()
    plt.figure(figsize=(6, 6))
    if total_frames > 0 and emotion_counts:
        labels = emotion_counts.keys()
        sizes = [emotion_counts[e] for e in labels]
        plt.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90, colors=plt.cm.Paired.colors)
        plt.title("Emotion Distribution Over Time")
    else:
        plt.text(0.5, 0.5, "No emotions detected", ha='center', va='center', fontsize=12)
        plt.title("No Data Available")

    # Save chart to disk
    chart_filename = f"chart_{student_id}.png"
    chart_path = os.path.join(RESULTS_FOLDER, chart_filename)
    plt.savefig(chart_path)

    # Also save chart to memory for DB
    chart_stream = io.BytesIO()
    plt.savefig(chart_stream, format='png')
    plt.close()
    chart_stream.seek(0)
    resultAnalysis = analyze_piechart(chart_filename)
    print(resultAnalysis)
    # Save or update in DB
    existing = EmotionAnalysis.query.filter_by(student_id=student_id).first()
    if existing:
        existing.top_emotion = top_emotion
        existing.second_emotion = second_emotion
        existing.distress_percentage = round(distress_percentage, 2)
        existing.alert_triggered = alert_triggered
        existing.chart_image = chart_stream.read()
        existing.timestamp = datetime.utcnow()
        existing.pie_chart_analysis = resultAnalysis
    else:
        new_record = EmotionAnalysis(
            student_id=student_id,
            top_emotion=top_emotion,
            second_emotion=second_emotion,
            distress_percentage=round(distress_percentage, 2),
            alert_triggered=alert_triggered,
            chart_image=chart_stream.read(),
            pie_chart_analysis=resultAnalysis
        )
        db.session.add(new_record)

    db.session.commit()

    return {
        'top_emotion': top_emotion,
        'second_emotion': second_emotion,
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
    """Generates personalized, structured feedback using Gemini based on emotional distress levels."""
    if distress_percentage >= 20:
        prompt = f"""
        A student has shown a high emotional distress level of {distress_percentage:.2f}% in the classroom.
        Do not mention any intro line such as Here's structured feedback based on the provided information just provide 
        the response.Generate structured and personalized feedback in plain text format (no markdown or bullet symbols).
        Include the following 4 labeled sections with exactly 2 points each:

        Personalized Feedback
        - A brief summary of the student’s emotional state and classroom engagement.

        Strengths
        - Two observed strengths based on emotional behavior.

        Areas for Growth
        - Two specific areas where the student may need support or improvement.

        Recommended Actions
        - Two practical and supportive actions the teacher can take to help the student.
        """

    elif distress_percentage >= 10:
        prompt = f"""
        A student has shown a moderate emotional distress level of {distress_percentage:.2f}% in the classroom. Do 
        not mention any intro line such as Here's structured feedback based on the provided information just provide 
        the response. Generate personalized, plain text feedback with the following 4 labeled sections and exactly 2 
        points in each:

        Personalized Feedback
        - A brief overview of the student’s emotional state and general behavior.

        Strengths
        - Two positive aspects of the student’s emotional performance.

        Areas for Growth
        - Two areas where the student could benefit from improvement.

        Recommended Actions
        - Two helpful and practical suggestions for the teacher to support the student further.
        """

    else:
        return (
            "Personalized Feedback\n"
            "The student shows excellent emotional balance and positive classroom behavior.\n"
            "They are likely comfortable and actively participating.\n\n"
            "Strengths\n"
            "Consistent emotional stability.\n"
            "Shows regular engagement and attention.\n\n"
            "Areas for Growth\n"
            "Could benefit from occasional new learning challenges.\n"
            "May enjoy more variety in learning activities.\n\n"
            "Recommended Actions\n"
            "Continue using interactive teaching methods.\n"
            "Incorporate occasional student-led activities."
        )

    # Generate structured feedback using Gemini
    model = genai.GenerativeModel("gemini-2.0-flash")
    response = model.generate_content(prompt)
    return response.text.strip()


def analyze_piechart(chartname):
    """Analyze the pie chart and return teacher feedback as a string"""
    chart_path = os.path.join(RESULTS_FOLDER, chartname)

    # Check if chart exists
    if not os.path.exists(chart_path):
        return "No chart available. Please run /analyze-emotion first."

    try:
        # Extract emotion data from the pie chart
        emotion_counts = extract_emotions_from_pie_chart(chart_path)
        if not emotion_counts:
            return "Error extracting emotions from pie chart."
        # Analyze extracted emotion data
        distress_percentage, neutral_happy_percentage = analyze_emotion_data(emotion_counts)
        # Generate feedback for teachers
        feedback = generate_teacher_feedback(distress_percentage)
        # Return feedback as plain string
        return feedback

    except Exception as e:
        return f"An error occurred: {str(e)}"


def parse_feedback_sections(feedback_text):
    sections = {
        "personalized_feedback": "",
        "strengths": "",
        "areas_for_growth": "",
        "recommended_actions": ""
    }

    # Define section headers and their respective keys
    section_map = {
        "Personalized Feedback": "personalized_feedback",
        "Strengths": "strengths",
        "Areas for Growth": "areas_for_growth",
        "Recommended Actions": "recommended_actions"
    }

    current_section = None
    lines = feedback_text.strip().splitlines()
    for line in lines:
        header = line.strip().rstrip(":")
        if header in section_map:
            current_section = section_map[header]
            continue
        elif current_section:
            sections[current_section] += line + "\n"

    # Strip trailing whitespace from each section
    for key in sections:
        sections[key] = sections[key].strip()

    return sections


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
    # # Create all database tables before running the app
    # with app.app_context():
    #     db.create_all()


    app.run(debug=True, host='0.0.0.0', port=5006)
