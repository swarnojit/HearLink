import os
import whisper
from langdetect import detect  # Language detection
from openai import OpenAI  # E2E OpenAI-compatible client

# --- Setup OpenAI Client for LLaMA 3 ---
client = OpenAI(
    base_url="https://infer.e2enetworks.net/project/p-5454/genai/llama_3_3_70b_instruct_fp8/v1",
    api_key=os.getenv("E2E_API_KEY")  # Or paste your API Key directly here (not recommended)
)

# --- Load Whisper Model for optional transcription ---
model = whisper.load_model("small", device="cuda")


def detect_language(text):
    """Detects the language of the given text using langdetect."""
    try:
        return detect(text)
    except Exception as e:
        print(f"❌ Language detection error: {e}")
        return "en"  # Default to English


def summarize_text(text, lang):
    """Summarizes the text into bullet points using LLaMA."""
    prompt = f"""- Do not include general or repetitive sentences.
Extract the most important points from the following text and format them into clear bullet points.
The response should be in {lang}.
- Use a structured format with bullet points. Keep it concise and include only essential information.
"""

    completion = client.chat.completions.create(
        model="llama_3_3_70b_instruct_fp8",
        messages=[
            {"role": "system", "content": prompt},
            {"role": "user", "content": text}
        ],
        temperature=0.5,
        max_tokens=1024,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=1,
        stream=True  # Streaming enabled
    )

    summary = ""
    for chunk in completion:
        if chunk.choices and chunk.choices[0].delta.content:
            summary += chunk.choices[0].delta.content

    return summary


def generate_flashcards(summary_text):
    """Formats the summary into structured flashcards."""
    flashcards = []
    summary_text = str(summary_text)  # Ensure it's a string
    points = summary_text.split("\n")
    
    for idx, point in enumerate(points, start=1):
        clean_point = point.strip()
        if clean_point:
            flashcards.append(f"📌 **Key Point {idx}:** {clean_point}")
    
    return "\n".join(flashcards)


# --- Main Script Start ---

# Check for available transcript
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

# Generate structured summary
print(f"🔎 Detected Language: {detected_lang.upper()}")
print("✨ Summarizing text...")
summary_text = summarize_text(text, detected_lang)

# Generate flashcards
flashcards = generate_flashcards(summary_text)

# Save outputs
with open("summary.txt", "w", encoding="utf-8") as file:
    file.write(summary_text)

with open("flashcards.txt", "w", encoding="utf-8") as file:
    file.write(flashcards)

print(f"\n✅ Summary & Flashcards Generated in: {detected_lang.upper()}")
print("\n📌 **Flashcards Preview:**\n")
print(flashcards)

print("\n📌 **Flashcards:**\n", flashcards)



