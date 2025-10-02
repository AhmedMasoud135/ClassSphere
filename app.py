import streamlit as st
from main import process_audio  # new function instead of process_url

st.set_page_config(page_title="Summarizer (Gemini)", layout="centered")
st.title("🎥 Audio Summarizer with Gemini")

st.write("Upload an audio file (mp3, wav, m4a) and get a summary powered by Whisper + Gemini.")

# File uploader
uploaded_file = st.file_uploader("Upload Audio File", type=["mp3", "wav", "m4a"])

if st.button("Summarize"):
    if not uploaded_file:
        st.error("Please upload an audio file.")
    else:
        # Save file temporarily
        with open("uploaded_audio.mp3", "wb") as f:
            f.write(uploaded_file.read())

        with st.spinner("Processing audio... please wait ⏳"):
            summary, transcript, quiz = process_audio("uploaded_audio.mp3")  # pass file path
        st.success("Done!")

        st.text_area("Summary:", value=summary, height=300, disabled=True)
        st.subheader("Quiz (5 questions)")
        st.text_area("Quiz:", quiz, height=300, disabled=True)
