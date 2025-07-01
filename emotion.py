import cv2
import os
from deepface import DeepFace
import time
from collections import defaultdict, Counter
import matplotlib.pyplot as plt
import numpy as np

# Constants
REGISTERED_DIR = "registered_faces"
alert_emotions = ["sad", "angry", "fear"]
distress_threshold = 20  # in %
update_interval = 60
monitor_duration = 10 * 60

# Face detector
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
cap = cv2.VideoCapture(0)

# Stats
emotion_counts = defaultdict(Counter)
total_frames = defaultdict(int)
last_alert_time = defaultdict(float)

# Enhance image contrast (for low light)
def enhance_contrast(img):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    clahe = cv2.createCLAHE(clipLimit=3.0)
    cl1 = clahe.apply(gray)
    return cv2.cvtColor(cl1, cv2.COLOR_GRAY2BGR)

# Recognize face using DeepFace (only keep known)
def recognize_face(face_img):
    try:
        result = DeepFace.find(img_path=face_img, db_path=REGISTERED_DIR, enforce_detection=False, silent=True)
        if len(result) > 0 and not result[0].empty:
            identity = os.path.basename(result[0].iloc[0]['identity']).split(".")[0]
            return identity
    except:
        pass
    return None  # Skip unknown

# Analyze emotion
def analyze_emotion(face_img):
    result = DeepFace.analyze(face_img, actions=['emotion'], enforce_detection=False)
    return result[0]['dominant_emotion']

# Generate individual reports only for registered users
def generate_report():
    with open("emotion.txt", "w", encoding="utf-8") as f:
        for person, counts in emotion_counts.items():
            frames = total_frames[person]
            if frames == 0:
                continue
            distress_frames = sum(counts[e] for e in alert_emotions)
            distress_percent = (distress_frames / frames) * 100

            f.write(f"\n👤 {person}\n")
            f.write(f"• Total Frames: {frames}\n")
            f.write(f"• Emotions: {dict(counts)}\n")
            f.write(f"• Distress Level: {distress_percent:.2f}%\n")

            if distress_percent >= distress_threshold:
                f.write(f"🚨 ALERT: {person} is in distress!\n")

            # Pie chart
            labels = list(counts.keys())
            sizes = [counts[e] for e in labels]
            if sizes:
                plt.figure(figsize=(4, 4))
                plt.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90)
                plt.title(f"{person}'s Emotion Distribution")
                plt.savefig(f"{person}_pie_chart.png")
                plt.close()

# Main loop
start_time = time.time()
while True:
    ret, frame = cap.read()
    if not ret:
        break

    enhanced_frame = enhance_contrast(frame)
    gray = cv2.cvtColor(enhanced_frame, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, 1.3, 5)

    for (x, y, w, h) in faces:
        face = enhanced_frame[y:y + h, x:x + w]
        try:
            name = recognize_face(face)

            # If not recognized, skip everything
            if not name:
                continue

            emotion = analyze_emotion(face)
            emotion_counts[name][emotion] += 1
            total_frames[name] += 1

            # Check for distress
            frames = total_frames[name]
            distress_frames = sum(emotion_counts[name][e] for e in alert_emotions)
            distress_percent = (distress_frames / frames) * 100 if frames else 0

            now = time.time()
            if distress_percent >= distress_threshold and now - last_alert_time[name] >= 60:
                print(f"\n🚨 ALERT: {name} is in distress ({distress_percent:.2f}%) 🚨")
                last_alert_time[name] = now

            # Draw face box and emotion
            color = (0, 0, 255) if emotion in alert_emotions else (0, 255, 0)
            cv2.rectangle(frame, (x, y), (x + w, y + h), color, 2)
            cv2.putText(frame, f"{name}: {emotion}", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)

        except Exception as e:
            print("Error:", e)

    # Show window
    cv2.imshow("Emotion Detection (Registered Only)", frame)

    # Auto-save report every update_interval
    elapsed = time.time() - start_time
    if elapsed % update_interval < 1:
        generate_report()

    if elapsed >= monitor_duration:
        print("\n⏰ Session ended. Resetting data.")
        generate_report()
        emotion_counts.clear()
        total_frames.clear()
        last_alert_time.clear()
        start_time = time.time()

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
