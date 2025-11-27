import re
from typing import List, Tuple

# --- Configuration ---
# Set a safe limit for TTS APIs. Using 4500 characters to be safely under 
# common 5000 character limits, ensuring full text fits in the request.
MAX_TTS_CHUNK_CHARACTERS = 4500

def chunk_text_for_narration(full_text: str) -> List[str]:
    """
    Takes a single string of text and divides it into smaller, coherent chunks 
    suitable for a Text-to-Speech (TTS) API, prioritizing paragraph breaks.
    
    Args:
        full_text (str): The entire document content as a single string.
        
    Returns:
        List[str]: A list of text chunks, each guaranteed to be under the 
                   MAX_TTS_CHUNK_CHARACTERS limit.
    """
    if not full_text.strip():
        return ["Document text is empty."]

    # 1. Split the text into major sections (paragraphs)
    # We use '\n\n' as the primary delimiter for semantic breaks.
    paragraphs = [p.strip() for p in full_text.split('\n\n') if p.strip()]
    
    tts_chunks = []
    current_chunk = ""
    
    for paragraph in paragraphs:
        
        # Check if adding the new paragraph exceeds the total allowed length
        # We add 2 to account for the necessary '\n\n' separator.
        if len(current_chunk) + len(paragraph) + 2 > MAX_TTS_CHUNK_CHARACTERS:
            
            # Current chunk is full. Save it.
            if current_chunk.strip():
                tts_chunks.append(current_chunk.strip())
            
            # Start a new chunk with the current paragraph.
            current_chunk = paragraph + "\n\n"
            
            # CRITICAL: Handle the case where a single paragraph is too long.
            if len(paragraph) > MAX_TTS_CHUNK_CHARACTERS:
                sub_chunks = split_oversized_paragraph_by_sentence(paragraph)
                tts_chunks.extend(sub_chunks)
                current_chunk = "" # Reset, as the oversized paragraph was handled.
        
        else:
            # Add the paragraph to the current chunk
            current_chunk += paragraph + "\n\n"
            
    # Add the final remaining chunk
    if current_chunk.strip():
        tts_chunks.append(current_chunk.strip())

    print("f \n\n-----------total chunks -----------------\n\n")
    print(len(tts_chunks))
        
    return tts_chunks

def split_oversized_paragraph_by_sentence(paragraph: str) -> List[str]:
    """
    Splits an extremely long paragraph into smaller sub-chunks by sentence, 
    used only as a fallback when paragraph chunking fails the size check.
    """
    # Split by sentence punctuation followed by space
    sentences = re.split(r'(?<=[.!?])\s+', paragraph) 
    
    sub_chunks = []
    current_sub_chunk = ""
    for sentence in sentences:
        if len(current_sub_chunk) + len(sentence) + 1 > MAX_TTS_CHUNK_CHARACTERS:
            # Sub-chunk is full, save it
            sub_chunks.append(current_sub_chunk.strip())
            current_sub_chunk = sentence + " "
        else:
            current_sub_chunk += sentence + " "
    
    # Add the final sub-chunk
    if current_sub_chunk.strip():
        sub_chunks.append(current_sub_chunk.strip())
        
    return sub_chunks



    # 1. Run the chunking process
    
    
    # 2. Display Results
    print(f"Total Text Length: {len(test_text)} characters")
    print(f"Generated {len(chunks)} Chunks for Narration (Max size: {MAX_TTS_CHUNK_CHARACTERS}):")
    print("=" * 60)
    
    for i, chunk in enumerate(chunks):
        print(f"CHUNK {i+1} (Length: {len(chunk)} chars, Starts with: '{chunk[:30]}...'):")
        # Check if the chunk is valid
        if len(chunk) > MAX_TTS_CHUNK_CHARACTERS:
            print("!!! WARNING: CHUNK EXCEEDS MAX SIZE !!!")
        else:
            print("Chunk size is valid.")
        print("-" * 30)