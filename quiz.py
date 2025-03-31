import streamlit as st
import os
import google.generativeai as genai
from dotenv import load_dotenv

# Load API key
load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Determine transcript file
translated_file = "translated_transcript.txt" if os.path.exists("translated_transcript.txt") else "translated.txt"

def read_transcript():
    """Read the translated transcript."""
    if os.path.exists(translated_file):
        with open(translated_file, "r", encoding="utf-8") as file:
            return file.read()
    else:
        st.error("No translated transcript file found!")
        return None

# Generate quizzes using AI
def generate_quiz(text):
    """Generate a structured quiz."""
    prompt = """
    You are an educational assistant. Create a multiple-choice quiz from the text.
    Provide exactly 5 questions, each with 4 options (A, B, C, D), and mark the correct answer separately.
    Keep the language the same as the input text.
    
    Format the output clearly like:
    1. Question text?
       A) Option 1
       B) Option 2
       C) Option 3
       D) Option 4
       
    After listing all 5 questions, provide the correct answers separately in this format:
    
    **Correct Answers:**
    1. X
    2. Y
    3. Z
    4. W
    5. V
    
    Text:
    """ + text

    model = genai.GenerativeModel("gemini-2.0-flash")
    response = model.generate_content(prompt)
    return response.text

# Generate structured exercises using AI
def generate_exercises(text):
    """Generate structured exercises without JSON."""
    prompt = """
    You are an educational assistant. Create structured exercises from the text.
    - 5 Fill-in-the-blank questions (missing words marked as '_____')
    - 5 Short-answer questions (1-2 sentence responses)
    - 5 Long-answer questions (detailed responses)
    
    Format the output clearly like:
    
    **Fill in the Blanks**
    1. Sentence with _____ missing.
    
    **Short Answer Questions**
    1. What is the importance of X?
    
    **Long Answer Questions**
    1. Explain how X impacts Y in detail.
    
    After listing all questions, provide the correct answers separately in this format:
    
    **Answers:**
    
    **Fill in the Blanks**
    1. Correct answer
    2. Correct answer
    
    **Short Answer Questions**
    1. Answer
    
    **Long Answer Questions**
    1. Answer
    
    Text:
    """ + text

    model = genai.GenerativeModel("gemini-2.0-flash")
    response = model.generate_content(prompt)
    return response.text

st.title("📚 Generate Quizzes & Exercises")

transcript_text = read_transcript()

if transcript_text:
    if st.button("Generate Quiz 📝"):
        quiz = generate_quiz(transcript_text)
        st.markdown("## 🏆 Quiz:")
        st.write(quiz)

    if st.button("Generate Exercises ✍️"):
        exercises = generate_exercises(transcript_text)
        st.markdown("## 📖 Exercises:")
        st.write(exercises)
