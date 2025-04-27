import os
import base64
import PyPDF2
import docx
import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI  # Import E2E OpenAI client

# Load environment variables
load_dotenv()  
client = OpenAI(
    base_url="https://infer.e2enetworks.net/project/p-5454/genai/llama_3_3_70b_instruct_fp8/v1",
    api_key=os.getenv("E2E_API_KEY")  # Use your API Key here
)

def extract_text_from_pdf(file):
    """Extract text from a PDF file."""
    pdf_reader = PyPDF2.PdfReader(file)
    text = "\n".join([page.extract_text() for page in pdf_reader.pages if page.extract_text()])
    return text

def extract_text_from_docx(file):
    """Extract text from a Word (.docx) file."""
    doc = docx.Document(file)
    text = "\n".join([para.text for para in doc.paragraphs])
    return text

def translate_notes_with_llama(notes_text, target_language):
    """Translate notes using LLaMA model."""
    prompt = f"Translate the following text into {target_language}:\n\n{notes_text}"

    # Call the OpenAI API (E2E) for translation using LLaMA
    completion = client.chat.completions.create(
        model='llama_3_3_70b_instruct_fp8',
        messages=[{"role":"user","content":prompt}],
        temperature=0.5,
        max_tokens=1024,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=1,
        stream=True
    )

    translated_notes = ""
    
    # Iterate over the chunks returned by the API and extract content correctly
    for chunk in completion:
        if hasattr(chunk, 'choices') and chunk.choices:  # Check if chunk has 'choices'
            # Access the content directly from the Choice object
            content = chunk.choices[0].delta.content if chunk.choices[0].delta else ""
            if content:
                translated_notes += content
    
    return translated_notes

def save_text_to_file(text, filename):
    """Save text to a file."""
    with open(filename, "w", encoding="utf-8") as file:
        file.write(text)

def get_download_link(file_content, file_name, label):
    """Generate a download link for a file."""
    b64 = base64.b64encode(file_content.encode()).decode()
    return f'<a href="data:file/txt;base64,{b64}" download="{file_name}">{label}</a>'

# Streamlit UI
st.title("AI-Powered Notes Translator")

# File uploader
uploaded_file = st.file_uploader("Upload your Notes (PDF or Word)", type=["pdf", "docx"])
target_language = st.selectbox(
    "Select Target Language:", 
    ["en", "hi", "ta", "bn", "te", "mr", "gu", "kn", "ml", "pa", "ur"]
)

if uploaded_file:
    file_extension = uploaded_file.name.split(".")[-1]

    # Extract text from file
    if file_extension == "pdf":
        notes_text = extract_text_from_pdf(uploaded_file)
    elif file_extension == "docx":
        notes_text = extract_text_from_docx(uploaded_file)
    else:
        st.error("Unsupported file format!")
        notes_text = ""

    if notes_text:
        st.markdown("## Extracted Notes:")
        st.write(notes_text)

        if st.button("Translate Notes"):
            st.markdown(f"### Translating Notes to {target_language.upper()}...")
            translated_notes = translate_notes_with_llama(notes_text, target_language)

            # Save translated notes
            file_name = "translated_notes.txt"
            save_text_to_file(translated_notes, file_name)
            st.success("Translation completed and saved!")

            # Display translated notes
            st.markdown("## Translated Notes:")
            st.write(translated_notes)

            # Download link
            st.markdown(get_download_link(translated_notes, file_name, "📥 Download Translated Notes"), unsafe_allow_html=True)
    else:
        st.warning("Could not extract text from the uploaded file.")
