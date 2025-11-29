import whisper
import os
import sys

# Add ffmpeg to PATH for Windows
ffmpeg_path = r"C:\ffmpeg\bin"
if ffmpeg_path not in os.environ["PATH"]:
    os.environ["PATH"] = ffmpeg_path + os.pathsep + os.environ["PATH"]

print("[INFO] Loading Whisper model...")
whisper_model = whisper.load_model("base")

def transcribe_audio(file_path, lang="en"):
    """Transcribe audio file to text using Whisper."""
    try:
        # Verify file exists
        if not os.path.exists(file_path):
            print(f"[ERROR] Audio file not found: {file_path}")
            return ""
        
        print(f"[INFO] Transcribing audio from: {file_path}")
        result = whisper_model.transcribe(file_path, language=lang, fp16=False)
        
        transcript = result.get("text", "")
        print(f"[SUCCESS] Transcription completed: {len(transcript)} characters")
        return transcript
        
    except Exception as e:
        print(f"[ERROR] Transcription failed: {e}")
        import traceback
        traceback.print_exc()
        return ""
