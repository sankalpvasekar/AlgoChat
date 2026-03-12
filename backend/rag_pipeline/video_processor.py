def chunk_transcript(snippets, max_words=400):
    """
    Groups transcript snippets into semantic chunks of roughly max_words.
    Each chunk retains the timestamp from its first snippet.
    
    Args:
        snippets: List of dicts with 'text' and 'start' keys.
        max_words: Target word count per chunk.
        
    Returns:
        List of dicts with 'text', 'timestamp', and 'video_id' (optional context).
    """
    chunks = []
    current_chunk_text = []
    current_chunk_start = 0.0
    current_word_count = 0
    
    if not snippets:
        return []

    for i, snippet in enumerate(snippets):
        text = snippet['text']
        timestamp = snippet['start']
        words = text.split()
        
        # If this is the start of a new chunk, record the timestamp
        if not current_chunk_text:
            current_chunk_start = timestamp
            
        current_chunk_text.append(text)
        current_word_count += len(words)
        
        # If we reached the word limit, or it's the last snippet
        if current_word_count >= max_words or i == len(snippets) - 1:
            chunks.append({
                "text": " ".join(current_chunk_text),
                "timestamp": current_chunk_start,
                "word_count": current_word_count
            })
            # Reset for next chunk
            current_chunk_text = []
            current_word_count = 0
            
    return chunks

if __name__ == "__main__":
    # Test case
    test_snippets = [
        {"text": "Hello world", "start": 0.0},
        {"text": "This is a test snippet.", "start": 5.0},
        {"text": "We are chunking this transcript.", "start": 10.0},
        {"text": "Another sentence here.", "start": 15.0},
    ]
    
    # Small max_words to force chunking
    result = chunk_transcript(test_snippets, max_words=5)
    import json
    print(json.dumps(result, indent=2))
