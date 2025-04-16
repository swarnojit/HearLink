import os
import google.generativeai as genai
import matplotlib.pyplot as plt
from collections import Counter
from PIL import Image

# Configure Gemini API
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

def extract_emotions_from_pie_chart(image_path):
    """Uses Gemini to extract text (emotion percentages) from the pie chart image."""
    model = genai.GenerativeModel("gemini-2.0-flash")
    
    with open(image_path, "rb") as img_file:
        image_data = img_file.read()
    
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
    
    response = model.generate_content([prompt, image_data])
    
    try:
        emotion_data = eval(response.text)  # Convert response to a dictionary
        return Counter(emotion_data)
    except Exception as e:
        print("Error parsing OCR output:", e)
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

def main():
    image_path = "emotion_pie_chart.png"  # Replace with the actual path
    if not os.path.exists(image_path):
        print("Error: Pie chart image not found.")
        return

    # Extract emotion data from the pie chart using Gemini
    emotion_counts = extract_emotions_from_pie_chart(image_path)
    if not emotion_counts:
        print("Error extracting emotions from pie chart.")
        return

    # Analyze extracted emotion data
    distress_percentage, neutral_happy_percentage = analyze_emotion_data(emotion_counts)

    # Generate feedback for teachers
    feedback = generate_teacher_feedback(distress_percentage)

    # Save feedback
    with open("teacher_feedback.txt", "w", encoding="utf-8") as file:
        file.write(feedback)

    print("\n✅ Teacher feedback generated and saved to teacher_feedback.txt")
    print(feedback)

    # Display the extracted emotion distribution as a pie chart
    plt.figure(figsize=(6, 6))
    labels = emotion_counts.keys()
    sizes = [emotion_counts[e] for e in labels]
    plt.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90, colors=plt.cm.Paired.colors)
    plt.title("Extracted Emotion Distribution")
    plt.show()

if __name__ == "__main__":
    main()
