import os
import ollama  # LLaMA for structured summarization
import whisper
from langdetect import detect  # Language detection

# Load Whisper Model
model = whisper.load_model("small", device="cuda")


def detect_language(text):
    """Detects the language of the given text using langdetect."""
    try:
        return detect(text)
    except:
        return "en"  # Default to English if detection fails


def summarize_text(text, lang):
    """Summarizes the text and extracts key points in bullet format."""
    prompt = f"""  - Do not include general or repetitive sentences.
    Extract the most important points from the following text and format them into clear bullet points.
    The response should be in {lang}.
    - Use a structured format with bullet points. Keep it concise and include only essential information.
    """

    response = ollama.chat(model="llama3", messages=[
        {"role": "system", "content": prompt},
        {"role": "user", "content": text}
    ])
    
    # Ensure the response is a string
    summary = str(response["message"]["content"])
    
    return summary


def generate_flashcards(summary_text):
    """Formats the summary into structured flashcards."""
    flashcards = []

    # Ensure summary_text is a string
    summary_text = str(summary_text)

    points = summary_text.split("\n")
    
    for idx, point in enumerate(points, start=1):
        clean_point = point.strip()
        if clean_point:
            flashcards.append(f"📌 **Key Point {idx}:** {clean_point}")
    
    return "\n".join(flashcards)


# Check if translated transcript exists, otherwise use the original
if os.path.exists("translated_transcript.txt") and os.path.getsize("translated_transcript.txt") > 0:
    transcript_file = "translated_transcript.txt"
elif os.path.exists("transcript.txt") and os.path.getsize("transcript.txt") > 0:
    transcript_file = "transcript.txt"
else:
    print("❌ No valid transcript found. Run `transcribe.py` first.")
    exit()

# Load text from transcript
with open(transcript_file, "r", encoding="utf-8") as file:
    text = file.read()

# Detect language
detected_lang = detect_language(text)

# Generate structured summary in bullet points
summary_text = summarize_text(text, detected_lang)
flashcards = generate_flashcards(summary_text)

# Save Summary & Flashcards
with open("summary.txt", "w", encoding="utf-8") as file:
    file.write(summary_text)

with open("flashcards.txt", "w", encoding="utf-8") as file:
    file.write(flashcards)

print(f"✅ Summary & Flashcards Generated in: {detected_lang.upper()}")
print("\n📌 **Flashcards:**\n", flashcards)



