import streamlit as st
import os
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# E2E Cloud API Setup
client = OpenAI(
    base_url="https://infer.e2enetworks.net/project/p-5454/genai/llama_3_3_70b_instruct_fp8/v1",
    api_key=os.getenv("E2E_API_KEY")  # Safely load from .env
)

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

def call_e2e_llama4(prompt):
    """Send prompt to E2E LLaMA 3.3 API and return the output."""
    try:
        response = client.chat.completions.create(
            model='llama_3_3_70b_instruct_fp8',
            messages=[{"role": "user", "content": prompt}],
            temperature=0.5,
            max_tokens=2048,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=1,
            stream=False  # Don't stream inside Streamlit
        )
        return response.choices[0].message.content
    except Exception as e:
        st.error(f"API Error: {e}")
        return None

def generate_quiz(text):
    """Generate a structured quiz."""
    prompt = f"""
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
    {text}
    """
    return call_e2e_llama4(prompt)

def generate_exercises(text):
    """Generate structured exercises."""
    prompt = f"""
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
    {text}
    """
    return call_e2e_llama4(prompt)

# --- Streamlit App ---
st.set_page_config(page_title="Quiz & Exercises Generator ", page_icon="📚")
st.title("📚 Generate Quizzes & Exercises ")

transcript_text = read_transcript()

if transcript_text:
    col1, col2 = st.columns(2)

    with col1:
        if st.button("Generate Quiz 📝"):
            with st.spinner("Generating quiz..."):
                quiz = generate_quiz(transcript_text)
            if quiz:
                st.markdown("## 🏆 Quiz:")
                st.write(quiz)

    with col2:
        if st.button("Generate Exercises ✍️"):
            with st.spinner("Generating exercises..."):
                exercises = generate_exercises(transcript_text)
            if exercises:
                st.markdown("## 📖 Exercises:")
                st.write(exercises)
else:
    st.warning("Please ensure a translated transcript file exists.")


