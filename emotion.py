import cv2
from deepface import DeepFace
from collections import Counter
import time
import matplotlib.pyplot as plt

# Load face cascade classifier
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

# Start capturing video
cap = cv2.VideoCapture(0)

# Emotion tracking variables
emotion_counts = Counter()
total_frames = 0
alert_emotions = ["sad", "angry", "fear"]
alert_triggered = False
start_time = time.time()
last_alert_time = start_time  # Track last alert time
monitor_duration = 10 * 60  # 10 minutes in seconds
update_interval = 60  # Update report every 1 minute
alert_check_interval = 60  # Alert only after 1 minute
distress_threshold = 15  # Now 15% instead of 25%
current_status = "Analyzing..."
current_emotion = "Neutral"

def generate_report():
    """Generates and saves an emotion report with a pie chart."""
    global emotion_counts, total_frames, current_status, last_alert_time, alert_triggered

    if total_frames == 0:
        current_status = "No emotions detected."
        return

    # Get top 2 emotions
    most_common = emotion_counts.most_common(2)
    top_emotion = most_common[0][0] if len(most_common) > 0 else "None"
    second_top_emotion = most_common[1][0] if len(most_common) > 1 else "None"

    # Calculate distress percentage
    distress_frames = sum(emotion_counts[e] for e in alert_emotions if e in emotion_counts)
    distress_percentage = (distress_frames / total_frames) * 100

    # Alert only if 1 min has passed since the last alert
    current_time = time.time()
    if distress_percentage >= distress_threshold and (current_time - last_alert_time) >= alert_check_interval:
        print("\n🚨 ALERT: Emotional distress detected! 🚨")
        print(f"⚠ Distress Level: {distress_percentage:.2f}%")
        last_alert_time = current_time  # Update last alert time
        alert_triggered = True  # Prevent multiple alerts in 1 min

    # Save report to file
    with open("emotion.txt", "w", encoding="utf-8") as file:
        file.write("🔹 **Emotion Analysis Report** 🔹\n")
        file.write(f"📌 Top Emotion: {top_emotion}\n")
        file.write(f"📌 Second Most Common Emotion: {second_top_emotion}\n")
        file.write(f"⚠ Emotional Distress Percentage: {distress_percentage:.2f}%\n")
        if distress_percentage >= distress_threshold:
            file.write("🚨 ALERT: Significant emotional distress detected! 🚨\n")

    print("\n✅ Report saved to emotion.txt")

    # Create pie chart
    plt.figure(figsize=(6, 6))
    labels = emotion_counts.keys()
    sizes = [emotion_counts[e] for e in labels]
    plt.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90, colors=plt.cm.Paired.colors)
    plt.title("Emotion Distribution Over Time")
    plt.show()

while True:
    # Capture frame-by-frame
    ret, frame = cap.read()
    if not ret:
        break

    # Convert frame to grayscale
    gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    rgb_frame = cv2.cvtColor(gray_frame, cv2.COLOR_GRAY2RGB)

    # Detect faces
    faces = face_cascade.detectMultiScale(gray_frame, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

    emotions_detected = []

    for (x, y, w, h) in faces:
        face_roi = rgb_frame[y:y + h, x:x + w]

        # Perform emotion analysis
        result = DeepFace.analyze(face_roi, actions=['emotion'], enforce_detection=False)

        # Get the dominant emotion
        emotion = result[0]['dominant_emotion']
        emotions_detected.append(emotion)
        current_emotion = emotion  # Update current face emotion

    # Update emotion counters
    emotion_counts.update(emotions_detected)
    total_frames += 1

    # Display the current emotion on the screen
    cv2.putText(frame, f"Current: {current_emotion}", (20, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)

    # Show frame
    cv2.imshow('Real-time Emotion Detection', frame)

    # Update report and pie chart every 1 minute
    elapsed_time = time.time() - start_time
    if elapsed_time % update_interval < 1:
        generate_report()

    # Stop monitoring after 10 minutes
    if elapsed_time >= monitor_duration:
        generate_report()  # Final report before reset
        print("\n🔴 Monitoring session ended. Resetting counts.\n")

        # Reset variables for the next 10-minute session
        emotion_counts.clear()
        total_frames = 0
        alert_triggered = False
        start_time = time.time()
        last_alert_time = start_time

    # Press 'q' to exit
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release capture and close windows
cap.release()
cv2.destroyAllWindows()
