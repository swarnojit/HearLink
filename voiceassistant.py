import os
import sqlite3
import streamlit as st
import fitz  # PyMuPDF
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
import google.generativeai as genai

# Setup Gemini
os.environ["GOOGLE_API_KEY"] = "your-gemini-api-key"  # Replace this
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Gemini response
def explain_with_gemini(query):
    model = genai.GenerativeModel("gemini-pro")
    response = model.generate_content(f"Explain this in simple and detailed terms: {query}")
    return response.text

# Load and chunk PDF
def load_pdf_chunks(pdf_path, chunk_size=500):
    try:
        doc = fitz.open(pdf_path)
        text = "".join(page.get_text() for page in doc)
        return [text[i:i + chunk_size] for i in range(0, len(text), chunk_size)]
    except Exception as e:
        st.warning(f"⚠️ Could not load PDF: {e}")
        return []

# Build FAISS index
def build_faiss_index(chunks, model):
    if not chunks:
        return None, None, None
    embeddings = model.encode(chunks)
    index = faiss.IndexFlatL2(embeddings.shape[1])
    index.add(np.array(embeddings))
    return index, embeddings, chunks

# Search in SQLite
def search_sqlite(query, db_path):
    if not os.path.exists(db_path):
        return None
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT content FROM knowledge WHERE content LIKE ?", (f"%{query}%",))
        result = cursor.fetchone()
        conn.close()
        return result[0] if result else None
    except Exception as e:
        st.warning(f"⚠️ Database error: {e}")
        return None

# Search in PDF (FAISS)
def search_in_pdf(query, model, index, chunks, embeddings, threshold=0.75):
    if not index or not chunks:
        return None
    query_vector = model.encode([query])
    distances, indices = index.search(np.array(query_vector), k=1)
    score = 1 - distances[0][0] / 4.0
    return chunks[indices[0][0]] if score >= threshold else None

# Streamlit app
def main():
    st.set_page_config(page_title="PDF + DB Chatbot", layout="wide")
    st.title("🤖 Smart Chatbot: PDF + SQLite + Gemini")
    st.markdown("Ask a question. If it's in your PDF or DB, you'll get an easy explanation.")

    # Paths (update these if needed)
    pdf_path = r"C:\Users\maitr\Documents\Meta Hackathon\student_notes.pdf"
    db_path = r"C:\Users\maitr\Documents\Meta Hackathon\classroom_data.db"

    # Load PDF and DB
    if "model" not in st.session_state:
        st.session_state.model = SentenceTransformer("all-MiniLM-L6-v2")
        st.session_state.chunks = load_pdf_chunks(pdf_path)
        st.session_state.index, st.session_state.embeddings, st.session_state.chunk_texts = build_faiss_index(
            st.session_state.chunks, st.session_state.model
        )

    query = st.text_input("💬 Ask your question:")

    if query:
        db_result = search_sqlite(query, db_path)
        pdf_result = search_in_pdf(
            query,
            st.session_state.model,
            st.session_state.index,
            st.session_state.chunk_texts,
            st.session_state.embeddings,
        )

        if db_result or pdf_result:
            st.success("✅ Match found! Getting explanation from Gemini...")
            response = explain_with_gemini(query)
            st.markdown("### 📘 Gemini Explanation")
            st.write(response)
        else:
            st.error("❌ Sorry, I cannot answer that as it's not found in either the PDF or database.")

if __name__ == "__main__":
    main()
