import os
import fitz  # PyMuPDF
import streamlit as st
import google.generativeai as genai

# === Gemini API Key and Model ===
genai.configure(api_key="")
gemini_model = genai.GenerativeModel("gemini-2.5-flash")

# === Static PDF Path ===
PDF_PATH = r"C:\Users\maitr\Documents\Meta Hackathon\student_notes.pdf"

# === Extract full text from the PDF ===
def extract_pdf_text(path):
    try:
        doc = fitz.open(path)
        return "\n".join([page.get_text() for page in doc])
    except Exception as e:
        st.error(f"Error reading PDF: {e}")
        return ""

# === Extract topic names using Gemini ===
def extract_topics(text):
    prompt = (
        "Read this academic text and extract only the main topic(s). "
        "Return them as a comma-separated list with no explanation.\n\n"
        + text
    )
    try:
        response = gemini_model.generate_content(prompt)
        return [t.strip().lower() for t in response.text.strip().split(",") if t.strip()]
    except Exception as e:
        st.error(f"Gemini failed to extract topics: {e}")
        return []

# === Let Gemini decide if question is relevant and answer accordingly ===
def answer_if_relevant(question, topics):
    prompt = (
        f"The user has studied the following topic(s): {', '.join(topics)}.\n"
        f"Based on that, answer the following question **only if it's clearly related to one of those topics**.\n"
        f"If it's related, give a short and simple answer.\n"
        f"If the question explicitly asks for an explanation, give a detailed one.\n"
        f"If it's not related at all, say: 'Sorry, your question is not related to the current topic.'\n\n"
        f"Question: {question}"
    )
    try:
        response = gemini_model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        return f"Gemini error: {e}"

# === Streamlit UI ===
def main():
    st.set_page_config(page_title="Gemini PDF Topic Chatbot", layout="centered")
    st.title("📘 Topic-Aware Gemini Chatbot")

    # Extract topic(s) once
    if "topics" not in st.session_state:
        with st.spinner("📖 Reading notes and extracting topic(s)..."):
            pdf_text = extract_pdf_text(PDF_PATH)
            st.session_state.topics = extract_topics(pdf_text)
        st.success("✅ Topics loaded successfully!")

    st.markdown("### 🧠 Topics Found in Notes:")
    st.write(", ".join(st.session_state.topics))

    # Input field
    question = st.text_input("💬 Ask your question:")

    if question:
        with st.spinner("🧠 Gemini is processing your question..."):
            answer = answer_if_relevant(question, st.session_state.topics)

        st.markdown("### ✨ Gemini Response")
        st.write(answer)

if __name__ == "__main__":
    main()

