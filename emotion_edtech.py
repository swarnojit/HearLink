
import cv2
from deepface import DeepFace
from collections import Counter, deque
import time
import matplotlib.pyplot as plt
import os
import json
import numpy as np

# ==== Configurable Alert Emotions ====
default_alert_emotions = ["sad", "angry", "fear"]
alert_emotions_file = "alert_emotions.txt"

if os.path.exists(alert_emotions_file):
    with open(alert_emotions_file, "r") as f:
        alert_emotions = [line.strip().lower() for line in f if line.strip()]
    if not alert_emotions:
        alert_emotions = default_alert_emotions
else:
    alert_emotions = default_alert_emotions

# ==== Initialize ====
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
cap = cv2.VideoCapture(0)
clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))

emotion_window = deque(maxlen=10)
emotion_counts = Counter()
total_frames = 0
frame_count = 0
current_emotion = "Analyzing..."
alert_triggered = False

start_time = time.time()
last_alert_time = start_time
monitor_duration = 10 * 60         # 10 minutes
update_interval = 60               # every 60 seconds
alert_check_interval = 60          # check alerts every 60 seconds
distress_threshold = 20            # in %

# ==== Emotion Stabilization ====
last_stable_emotion = "neutral"
neutral_sustain_count = 0
emotion_threshold = 3  # Number of consistent appearances to update

# ==== Helper Functions ====

def smooth_emotion(window):
    if not window:
        return "neutral"
    counter = Counter(window)
    return counter.most_common(1)[0][0]

def adjust_gamma(image, gamma=2.0):
    if image.dtype != np.uint8:
        image = np.clip(image, 0, 255).astype(np.uint8)

    inv_gamma = 1.0 / gamma
    table = np.array([(i / 255.0) ** inv_gamma * 255 for i in range(256)]).astype("uint8")
    return cv2.LUT(image, table)

def generate_report():
    global emotion_counts, total_frames, last_alert_time, alert_triggered

    if total_frames == 0:
        return

    most_common = emotion_counts.most_common(2)
    top_emotion = most_common[0][0] if len(most_common) > 0 else "None"
    second_top_emotion = most_common[1][0] if len(most_common) > 1 else "None"

    distress_frames = sum(emotion_counts[e] for e in alert_emotions if e in emotion_counts)
    distress_percentage = (distress_frames / total_frames) * 100

    current_time = time.time()
    if distress_percentage >= distress_threshold and (current_time - last_alert_time) >= alert_check_interval:
        print("\n🚨 ALERT: Emotional distress detected!")
        print(f"⚠ Distress Level: {distress_percentage:.2f}%")
        last_alert_time = current_time
        alert_triggered = True

    with open("emotion.txt", "w", encoding="utf-8") as f:
        f.write("🔹 Emotion Analysis Report 🔹\n")
        f.write(f"📌 Top Emotion: {top_emotion}\n")
        f.write(f"📌 Second Most Common Emotion: {second_top_emotion}\n")
        f.write(f"⚠ Emotional Distress Percentage: {distress_percentage:.2f}%\n")
        if distress_percentage >= distress_threshold:
            f.write("🚨 ALERT: Significant emotional distress detected! 🚨\n")

    with open("emotion_data.json", "w", encoding="utf-8") as jf:
        json.dump(dict(emotion_counts), jf, indent=4)

    print("✅ Report saved to emotion.txt and emotion_data.json")

    plt.figure(figsize=(6, 6))
    labels = emotion_counts.keys()
    sizes = [emotion_counts[e] for e in labels]
    plt.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90, colors=plt.cm.Paired.colors)
    plt.title("Emotion Distribution Over Time")
    plt.savefig("emotion_pie_chart.png")
    plt.close()
    print("✅ Pie chart saved as emotion_pie_chart.png")

# ==== Main Loop ====

while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame_count += 1

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    enhanced_gray = clahe.apply(gray)

    # 🔆 Dynamic gamma correction based on brightness
    avg_brightness = np.mean(enhanced_gray)
    if avg_brightness < 50:
        gamma_value = 2.5
    elif avg_brightness < 80:
        gamma_value = 2.0
    else:
        gamma_value = 1.5

    enhanced_gray = adjust_gamma(enhanced_gray, gamma=gamma_value)

    rgb = cv2.cvtColor(enhanced_gray, cv2.COLOR_GRAY2RGB)

    faces = face_cascade.detectMultiScale(enhanced_gray, scaleFactor=1.1, minNeighbors=5)
    emotions_this_frame = []

    for (x, y, w, h) in faces:
        face_roi = rgb[y:y+h, x:x+w]
        try:
            result = DeepFace.analyze(
                face_roi,
                actions=['emotion'],
                enforce_detection=False,
                detector_backend='opencv'
            )
            emotion = result[0]['dominant_emotion']
            emotions_this_frame.append(emotion)
        except Exception as e:
            print(f"Emotion detection error: {e}")

    if emotions_this_frame:
        for emotion in emotions_this_frame:
            emotion_window.append(emotion)

        smoothed = smooth_emotion(emotion_window)
        freq = emotion_window.count(smoothed)

        if smoothed == "neutral":
            neutral_sustain_count += 1
        else:
            neutral_sustain_count = 0

        if freq >= emotion_threshold or smoothed == last_stable_emotion:
            last_stable_emotion = smoothed

        emotion_counts.update([last_stable_emotion])
        total_frames += 1
        current_emotion = last_stable_emotion

    cv2.putText(frame, f"Emotion: {current_emotion}", (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)

    cv2.imshow("Emotion Detection", frame)

    elapsed_time = time.time() - start_time

    if int(elapsed_time) % update_interval == 0:
        generate_report()

    if elapsed_time >= monitor_duration:
        generate_report()
        print("\n🔴 Monitoring session ended. Resetting data...\n")
        emotion_counts.clear()
        total_frames = 0
        alert_triggered = False
        start_time = time.time()
        last_alert_time = start_time

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
