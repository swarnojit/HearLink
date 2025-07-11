import os
import google.generativeai as genai
import matplotlib.pyplot as plt
from collections import Counter
from PIL import Image
import json

# Configure Gemini API
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

def extract_emotions_from_pie_chart(image_path):
    model = genai.GenerativeModel("gemini-2.0-flash")

    try:
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
        }"""
        response = model.generate_content([prompt, image])
        json_str = response.text[response.text.find("{"):response.text.rfind("}")+1]
        emotion_data = json.loads(json_str)
        return Counter(emotion_data)
    except Exception as e:
        print("Error parsing OCR output:", e)
        return None

def analyze_emotion_data(emotion_counts):
    total_frames = sum(emotion_counts.values())
    distress_emotions = ["sad", "angry", "fear", "disgust"]
    distress_percentage = sum(emotion_counts.get(e, 0) for e in distress_emotions) / total_frames * 100
    neutral_happy_percentage = (emotion_counts.get("neutral", 0) + emotion_counts.get("happy", 0)) / total_frames * 100
    return distress_percentage, neutral_happy_percentage

def generate_teacher_feedback(distress_percentage):
    if distress_percentage >= 20:
        prompt = f"""
        The classroom analysis shows a high emotional distress level of {distress_percentage:.2f}%. 
        Provide structured feedback for the teacher including:
        1. Possible reasons why students may be experiencing distress.
        2. Practical steps the teacher can take to create a more inclusive and engaging environment.
        3. Expected improvement percentage if these steps are implemented.
        """
    elif distress_percentage >= 10:
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

def read_txt_emotion_file(file_path):
    if not os.path.exists(file_path):
        print("❌ Emotion text file not found.")
        return None, None

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
        lines = content.splitlines()
        distress_line = next((line for line in lines if "Distress Level" in line), None)
        if distress_line:
            percent = float(distress_line.split(":")[-1].replace("%", "").strip())
            return content, percent
        else:
            print("❌ Distress level not found in file.")
            return content, None
    except Exception as e:
        print("❌ Error reading emotion.txt:", e)
        return None, None

def main():
    name = input("Enter the student's name: ").strip().lower()
    image_path = f"{name}_pie_chart.png"
    txt_path = f"{name}_emotion.txt"

    if not os.path.exists(image_path):
        print("❌ Pie chart image not found.")
        return

    txt_content, txt_distress = read_txt_emotion_file(txt_path)
    if txt_content is None or txt_distress is None:
        return

    emotion_counts = extract_emotions_from_pie_chart(image_path)
    if not emotion_counts:
        print("❌ Error extracting emotions from pie chart.")
        return

    pie_distress, _ = analyze_emotion_data(emotion_counts)

    # Alignment check
    if abs(pie_distress - txt_distress) > 10:
        print("⚠️ Pie chart and text distress levels differ significantly. Manual review recommended.")
        return

    # Generate feedback if aligned
    feedback = generate_teacher_feedback((pie_distress + txt_distress) / 2)

    with open("teacher_feedback.txt", "w", encoding="utf-8") as file:
        file.write(feedback)

    print("\n✅ Teacher feedback generated and saved to teacher_feedback.txt")
    print(feedback)

    # Display extracted pie chart
    plt.figure(figsize=(6, 6))
    labels = emotion_counts.keys()
    sizes = [emotion_counts[e] for e in labels]
    plt.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90, colors=plt.cm.Paired.colors)
    plt.title("Extracted Emotion Distribution")
    plt.show()

if __name__ == "__main__":
    main()
