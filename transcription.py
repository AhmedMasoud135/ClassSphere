import whisper
print("[INFO] Loading Whisper model...")
whisper_model = whisper.load_model("base")
def transcribe_audio(file_path, lang="en"):
    """Transcribe audio file to text using Whisper."""
    try:
        print("[INFO] Transcribing audio...")
        result = whisper_model.transcribe(file_path, language=lang)
        print("[INFO] Transcription done.")
        return result.get("text", "")
    except Exception as e:
        print(f"[ERROR] Transcription failed: {e}")
        return ""
