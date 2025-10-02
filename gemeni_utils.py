from config import GEMINI_API_KEY, GEMINI_MODEL
from google import genai
from google.genai import types
from text_utils import chunk_text_words

client = genai.Client(api_key=GEMINI_API_KEY)
def get_response_text(resp):
    """Extract text from Gemini API response safely."""
    try:
        if hasattr(resp, "text") and resp.text:
            return resp.text.strip()
    except Exception as e:
        print("[ERROR] Response extraction failed:", e)
    return ""

def summarize_with_gemini(text, model=GEMINI_MODEL, max_output_tokens=1024):
    """Summarize transcript with Gemini (handles long text)."""
    if not text.strip():
        return "[ERROR] Empty transcript."

    words = text.split()
    if len(words) <= 1200:
        prompt = (
            "Summarize the following transcript into 6–10 sentences. "
            "Focus on key concepts only and ignore promotional content "
            "(like books, subscriptions, or personal ads). "
            "Do not return the corrected transcript, only the summary.\n\n"
            f"Transcript:\n{text}"
        )
        resp = client.models.generate_content(
            model=model,
            contents=prompt
        )
        return get_response_text(resp)

    # For long transcripts, split and summarize in chunks
    print("[INFO] Transcript too long, summarizing in chunks...")
    chunk_summaries = []
    for i, chunk in enumerate(chunk_text_words(text, max_words=1200), start=1):
        prompt = (
            "Summarize this part in 3–4 sentences. "
            "Keep only the important points, ignore promotions.\n\n"
            f"{chunk}"
        )
        resp = client.models.generate_content(
            model=model,
            contents=prompt
        )
        chunk_summaries.append(get_response_text(resp))

    combined = "\n\n".join(chunk_summaries)
    final_prompt = (
        "Combine these partial summaries into a single unified summary (6–10 sentences). "
        "Make it smooth, natural, and free of promotional or irrelevant content:\n\n"
        f"{combined}"
    )

    resp_final = client.models.generate_content(
        model=model,
        contents=final_prompt
    )
    return get_response_text(resp_final)



def quiz_with_gemini(transcript, n_questions=5, model=GEMINI_MODEL):
    prompt = (
        f"Based on the following transcript, create {n_questions} multiple-choice quiz questions. "
        "Rules:\n"
        "- Each question must have 4 options (A, B, C, D).\n"
        "- Randomize the correct answer (not always the same letter).\n"
        "- At the end of each question, indicate the correct option clearly like: Correct Answer: B\n"
        "- Keep questions short and relevant to the transcript.\n\n"
        f"Transcript:\n{transcript}"
    )
    resp = client.models.generate_content(model=model, contents=prompt)
    return get_response_text(resp)

