from transcription import transcribe_audio
from gemeni_utils import summarize_with_gemini, quiz_with_gemini

def process_audio(audio_file, lang="en"):
    """Main pipeline: transcribe → summarize → quiz."""
    transcript = transcribe_audio(audio_file, lang)
    if not transcript:
        return "[ERROR] Failed to transcribe audio.", "", ""

    summary = summarize_with_gemini(transcript)
    quiz = quiz_with_gemini(transcript)

    print("\n=== TRANSCRIPT (preview) ===\n")
    print(transcript[:800] + ("..." if len(transcript) > 800 else ""))
    print("\n=== SUMMARY ===\n")
    print(summary)
    print("\n=== QUIZ ===\n")
    print(quiz)

    return summary, transcript, quiz

if __name__ == "__main__":
    process_audio("lesson.mp3")