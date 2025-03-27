import cv2
from deepface import DeepFace
from collections import Counter
import time
import matplotlib.pyplot as plt
# import emotion_alert # Removing this as we integrate the logic here

# --- Configuration ---
ALERT_EMOTIONS = ["sad", "angry", "fear"] # Emotions indicating potential misunderstanding/distress
DISTRESS_THRESHOLD_PERCENT = 15.0        # Trigger alert/stronger recommendations if % of ALERT_EMOTIONS exceeds this
MONITOR_DURATION_SECONDS = 10 * 60       # Duration of each monitoring session
REPORT_INTERVAL_SECONDS = 60           # How often to generate a report and recommendations
ALERT_COOLDOWN_SECONDS = 60            # Minimum time between distress alerts

# --- LLM/AI Enhancement Ideas (Comments) ---
# 1. Contextual Understanding: An LLM could take the current topic being taught (if provided)
#    and tailor recommendations more specifically. E.g., "For math concepts, try visual block representation."
# 2. Nuanced Emotion Interpretation: LLMs could interpret combinations of emotions or the sequence
#    of emotions over time for more sophisticated insights beyond simple percentages.
# 3. Adaptive Learning: An LLM could learn which recommendations are most effective for specific
#    students or contexts over time (requires a feedback loop).
# 4. Natural Language Generation: Generate more fluid and varied recommendation text.

# --- Function to Generate Teacher Recommendations ---

def generate_teacher_recommendations(emotion_counts, total_frames, alert_emotions, distress_threshold):
    """
    Analyzes emotion data and generates actionable recommendations for the teacher.
    Focuses on adjustments beneficial for deaf students' understanding.

    Args:
        emotion_counts (Counter): Counts of each detected emotion.
        total_frames (int): Total frames analyzed in the current period.
        alert_emotions (list): List of emotions considered negative/distressful.
        distress_threshold (float): Percentage threshold for triggering distress-related advice.

    Returns:
        list: A list of strings, each representing a recommendation bullet point.
    """
    recommendations = []

    if total_frames == 0:
        recommendations.append("No face detected or emotions analyzed yet.")
        return recommendations

    # Calculate distress percentage
    distress_frames = sum(emotion_counts.get(e, 0) for e in alert_emotions)
    distress_percentage = (distress_frames / total_frames) * 100 if total_frames > 0 else 0

    # Get top emotion
    most_common = emotion_counts.most_common(1)
    top_emotion = most_common[0][0] if most_common else "None"
    top_emotion_percentage = (most_common[0][1] / total_frames) * 100 if most_common else 0

    # --- Recommendation Logic ---

    if distress_percentage >= distress_threshold:
        recommendations.append(f"High Distress ({distress_percentage:.1f}%). Student may be significantly confused or overwhelmed.")
        recommendations.append("- **IMMEDIATE CHECK:** Pause and directly check for understanding. Use clear, simple questions or ask the student to explain back.")
        recommendations.append("- **SIMPLIFY:** Break down the current concept into smaller, more manageable steps.")
        recommendations.append("- **VISUAL AIDS:** Increase the use of visual aids (diagrams, charts, real objects, relevant BSL/ASL visuals).")
        recommendations.append("- **PACE:** Slow down the pace of instruction.")
        # LLM Idea: Could suggest specific visual aids based on the topic.

    elif top_emotion in alert_emotions:
        recommendations.append(f"Dominant Emotion: {top_emotion} ({top_emotion_percentage:.1f}%). This might indicate difficulty.")
        if top_emotion == "sad" or top_emotion == "fear":
            recommendations.append("- **REPHRASE:** Explain the concept using different signs, vocabulary, or sentence structures.")
            recommendations.append("- **EXAMPLES:** Provide more concrete examples relevant to the topic.")
            recommendations.append("- **VISUAL CHECK:** Ensure the student can clearly see your signs, facial expressions, and any visual materials.")
            recommendations.append("- **ENCOURAGE QUESTIONS:** Remind the student it's okay to ask for clarification.")
            # LLM Idea: Could suggest alternative phrasing or specific example types.
        elif top_emotion == "angry":
            recommendations.append("- **ACKNOWLEDGE:** Gently acknowledge the potential frustration ('This part can be tricky').")
            recommendations.append("- **BREAK DOWN TASK:** If it's an activity, break it into smaller steps.")
            recommendations.append("- **CHECK RESOURCES:** Ensure any required tools or materials are working correctly and are accessible.")
            recommendations.append("- **OFFER A BRIEF PAUSE:** A short mental break might help reset focus.")
            # LLM Idea: Could analyze if frustration correlates with specific parts of the lesson.

    elif top_emotion == "neutral" and top_emotion_percentage > 75: # High percentage of neutral might mean disengagement
         recommendations.append(f"Dominant Emotion: Neutral ({top_emotion_percentage:.1f}%). Consider if student is engaged.")
         recommendations.append("- **INTERACTIVITY:** Try incorporating a question, a quick poll, or a related interactive element.")
         recommendations.append("- **CONNECT:** Briefly relate the topic to student interests if possible.")
         recommendations.append("- **VARY MODALITY:** If just lecturing/signing, add a visual or a short activity.")
         # LLM Idea: Could suggest engagement techniques specific to deaf learners.

    elif top_emotion == "happy" or top_emotion == "surprise":
        recommendations.append(f"Positive Emotion ({top_emotion}) Detected. Student seems engaged or understands.")
        recommendations.append("- **MAINTAIN:** Continue with the current teaching approach for this segment.")
        recommendations.append("- **POSITIVE REINFORCEMENT:** Acknowledge understanding or correct answers.")

    else: # Covers cases with low distress and non-negative dominant emotions (or multiple mixed)
         recommendations.append("Emotions appear generally stable. Monitor for changes.")
         recommendations.append("- **CONTINUE MONITORING:** Keep observing facial cues and checking for understanding periodically.")

    # Generic good practices for teaching deaf students
    if not recommendations: # If no specific trigger, add general tips
        recommendations.append("General Tips:")
    recommendations.append("- Ensure good lighting on the teacher's face for lip-reading and facial expressions.")
    recommendations.append("- Use clear and appropriately paced Sign Language (if applicable).")
    recommendations.append("- Regularly use visual aids and check for visual confirmation of understanding.")

    return recommendations


# --- Main Application Code (Adapted from your original) ---

# Load face cascade classifier
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

# Start capturing video
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("Error: Could not open video capture device.")
    exit()

# Emotion tracking variables
emotion_counts = Counter()
total_frames = 0
# alert_emotions = ["sad", "angry", "fear"] # Defined in Configuration
alert_triggered_in_interval = False # Track if alert happened within the current report interval
start_time = time.time()
last_report_time = start_time
last_alert_time = -ALERT_COOLDOWN_SECONDS # Allow alert immediately at start if needed
# monitor_duration = MONITOR_DURATION_SECONDS # Defined in Configuration
# update_interval = REPORT_INTERVAL_SECONDS # Defined in Configuration
# alert_check_interval = ALERT_COOLDOWN_SECONDS # Defined in Configuration
# distress_threshold = DISTRESS_THRESHOLD_PERCENT # Defined in Configuration
current_status = "Initializing..."
current_emotion_display = "None"

def generate_report_and_recommendations():
    """Generates emotion report, saves it, shows plot, and provides teacher recommendations."""
    global emotion_counts, total_frames, current_status, last_alert_time, alert_triggered_in_interval, start_time

    if total_frames == 0:
        current_status = "No emotions detected in the last interval."
        print(f"\n--- Report @ {time.strftime('%H:%M:%S')} ---")
        print(current_status)
        # Generate recommendations even if no frames, might give "No face detected..."
        recommendations = generate_teacher_recommendations(emotion_counts, total_frames, ALERT_EMOTIONS, DISTRESS_THRESHOLD_PERCENT)
        print("\n💡 Teacher Recommendations:")
        for rec in recommendations:
            print(f"   {rec}")
        print("--------------------------------\n")
        return # Don't proceed with calculations if no frames

    # --- Calculations ---
    most_common = emotion_counts.most_common(2)
    top_emotion = most_common[0][0] if len(most_common) > 0 else "None"
    second_top_emotion = most_common[1][0] if len(most_common) > 1 else "None"

    distress_frames = sum(emotion_counts.get(e, 0) for e in ALERT_EMOTIONS)
    distress_percentage = (distress_frames / total_frames) * 100

    current_time = time.time()
    alert_now = False
    if distress_percentage >= DISTRESS_THRESHOLD_PERCENT and (current_time - last_alert_time) >= ALERT_COOLDOWN_SECONDS:
        alert_now = True
        last_alert_time = current_time
        alert_triggered_in_interval = True # Mark that alert happened

    # --- Generate Recommendations ---
    print(f"\n--- Report @ {time.strftime('%H:%M:%S')} ---")
    if alert_now:
        print("🚨 ALERT: Potential Student Difficulty Detected! 🚨")

    recommendations = generate_teacher_recommendations(emotion_counts, total_frames, ALERT_EMOTIONS, DISTRESS_THRESHOLD_PERCENT)
    print("\n💡 Teacher Recommendations:")
    for rec in recommendations:
        print(f"   {rec}")

    # --- Save Report File ---
    try:
        with open("emotion_report.txt", "a", encoding="utf-8") as file: # Append mode
            file.write(f"\n--- Report @ {time.strftime('%Y-%m-%d %H:%M:%S')} ---\n")
            file.write(f"Interval Duration: {REPORT_INTERVAL_SECONDS}s\n")
            file.write(f"Frames Analyzed: {total_frames}\n")
            file.write(f"Top Emotion: {top_emotion} ({emotion_counts.get(top_emotion, 0)} frames)\n")
            file.write(f"Second Emotion: {second_top_emotion} ({emotion_counts.get(second_top_emotion, 0)} frames)\n")
            file.write(f"Distress Emotions ({', '.join(ALERT_EMOTIONS)}) Percentage: {distress_percentage:.2f}%\n")
            if alert_triggered_in_interval:
                file.write("🚨 ALERT Triggered in this interval due to high distress percentage.\n")
            file.write("\nRecommendations Given:\n")
            for rec in recommendations:
                file.write(f"- {rec}\n")
            file.write("------------------------------------\n")
        print("\n✅ Report appended to emotion_report.txt")
    except Exception as e:
        print(f"\n❌ Error saving report file: {e}")

    # --- Generate Pie Chart ---
    try:
        plt.figure(figsize=(6, 6))
        labels = list(emotion_counts.keys())
        sizes = [emotion_counts[e] for e in labels]
         # Avoid plotting if no data
        if labels and sizes:
            plt.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90, colors=plt.cm.Paired.colors)
            plt.title(f"Emotion Distribution ({time.strftime('%H:%M:%S')})")
            plt.savefig(f"emotion_pie_{time.strftime('%Y%m%d_%H%M%S')}.png") # Save with timestamp
            print(f"✅ Pie chart saved as emotion_pie_{time.strftime('%Y%m%d_%H%M%S')}.png")
            # plt.show() # Maybe don't show interactively, just save? Or make optional.
            plt.close() # Close the figure to free memory
        else:
            print("ℹ️ No emotion data to plot for this interval.")
    except Exception as e:
        print(f"\n❌ Error generating pie chart: {e}")

    # --- Reset for next interval ---
    print("--------------------------------\n")
    emotion_counts.clear()
    total_frames = 0
    alert_triggered_in_interval = False


# --- Main Loop ---
session_start_time = time.time()
print("Starting Real-time Emotion Monitoring...")

while True:
    # Capture frame-by-frame
    ret, frame = cap.read()
    if not ret:
        print("Error: Can't receive frame (stream end?). Exiting ...")
        break

    # Prepare frame
    gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB) # DeepFace prefers RGB

    # Detect faces
    faces = face_cascade.detectMultiScale(gray_frame, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

    current_emotions_in_frame = []

    # Process each detected face
    for (x, y, w, h) in faces:
        face_roi = rgb_frame[y:y + h, x:x + w]

        try:
            # Perform emotion analysis using DeepFace
            # Added backend selection for potentially faster/lighter models if needed
            result = DeepFace.analyze(face_roi,
                                      actions=['emotion'],
                                      enforce_detection=False,
                                      detector_backend='opencv', # or 'ssd', 'mtcnn', etc.
                                      silent=True) # Suppress DeepFace progress bars

            # Check if result is valid (list and has elements)
            if isinstance(result, list) and len(result) > 0:
                emotion = result[0]['dominant_emotion']
                current_emotions_in_frame.append(emotion)

                # Draw rectangle and emotion text on the frame
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                cv2.putText(frame, emotion, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            else:
                 # Optionally draw a box even if emotion analysis failed for the ROI
                 cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 1) # Red box for failed analysis

        except Exception as e:
            # Log errors if DeepFace fails for a face ROI
            # print(f"Error analyzing face ROI: {e}") # Can be noisy, enable for debugging
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 1) # Red box for error


    # Update overall emotion counts for the interval
    if current_emotions_in_frame:
        emotion_counts.update(current_emotions_in_frame)
        total_frames += len(current_emotions_in_frame) # Count per face analyzed
        current_emotion_display = ", ".join(set(current_emotions_in_frame)) # Show unique emotions in frame
    else:
        current_emotion_display = "None"


    # Display status on the frame
    elapsed_session_time = time.time() - session_start_time
    cv2.putText(frame, f"Status: Monitoring | Time: {int(elapsed_session_time)}s", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
    cv2.putText(frame, f"Emotions Now: {current_emotion_display}", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 1)

    # Show frame
    cv2.imshow('Real-time Emotion Detection for Teacher Feedback', frame)

    # Check if it's time to generate report and recommendations
    current_loop_time = time.time()
    if (current_loop_time - last_report_time) >= REPORT_INTERVAL_SECONDS:
        generate_report_and_recommendations()
        last_report_time = current_loop_time # Reset report timer

    # Check for overall monitoring duration (optional, if you want sessions)
    # if elapsed_session_time >= MONITOR_DURATION_SECONDS:
    #     print(f"\n--- Monitoring Session Ended ({MONITOR_DURATION_SECONDS}s) ---")
    #     generate_report_and_recommendations() # Final report for the session
    #     # Reset session variables if you want continuous sessions
    #     session_start_time = time.time()
    #     last_report_time = session_start_time
    #     last_alert_time = session_start_time - ALERT_COOLDOWN_SECONDS
    #     print("--- Starting New Monitoring Session ---")


    # Press 'q' to exit
    if cv2.waitKey(1) & 0xFF == ord('q'):
        print("Exiting application...")
        break

# --- Cleanup ---
cap.release()
cv2.destroyAllWindows()

# Final report if loop broken by 'q' before interval ends
print("\n--- Final Report on Exit ---")
generate_report_and_recommendations()
print("Application finished.")