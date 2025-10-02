def chunk_text_words(text, max_words=1200):
    """Split text into word-based chunks."""
    words = text.split()
    for i in range(0, len(words), max_words):
        yield " ".join(words[i:i+max_words])