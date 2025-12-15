def chunk_text(text: str, chunk_size: int = 500) -> list[str]:
    """
    Splits text into chunks of approximately `chunk_size` words.
    Simple whitespace splitting fits the requirement for 'tokens' roughly without heavy dependencies.
    """
    if not text:
        return []
        
    words = text.split()
    chunks = []
    current_chunk = []
    current_count = 0
    
    for word in words:
        current_chunk.append(word)
        current_count += 1
        
        if current_count >= chunk_size:
            chunks.append(" ".join(current_chunk))
            current_chunk = []
            current_count = 0
            
    # Add remaining words
    if current_chunk:
        chunks.append(" ".join(current_chunk))
        
    return chunks
