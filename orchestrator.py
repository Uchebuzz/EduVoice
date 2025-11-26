import os
import sys

from PdfReaderAgent import process_pdf_from_ui 
from DocumentReader import process_word_doc_from_ui

def determine_file_extension(file_path: str) -> str:
    """
    Extracts the file extension from a given path and returns it lowercased.
    """
    return os.path.splitext(file_path)[1].lower()

def run_document_orchestrator(file_path: str) -> str:
    print("Orchestrator running ---")
    """
    The central router that selects the correct document processing agent 
    based on the file's extension.
    
    Args:
        file_path (str): The absolute or relative path to the file on disk.
        
    Returns:
        str: The final processed output from the chosen agent.
    """
    if not file_path:
        return "ERROR: No file path provided."

    # Step 1: Validate file existence
    if not os.path.exists(file_path):
        return f"ERROR: File not found at path: '{file_path}'. Please check the file path."

    ext = determine_file_extension(file_path)
    
    print(f"Orchestrator received file path: {file_path}")
    print(f"Detected extension: {ext}")
    
    result = ""
    
    # --- Step 2: Routing Logic ---
    if ext == ".docx" or ext == ".doc":
        print("Routing to DocReaderAgent...")
        # Delegation: The DocReaderAgent function handles the full DOCX/DOC processing logic
        result = process_word_doc_from_ui(file_path)
    
    elif ext == ".pdf":
        print("Routing to PdfReaderAgent...")
        # Delegation: The PdfReaderAgent function handles the full PDF processing logic
        result = process_pdf_from_ui(file_path)

    else:
        # Handle unsupported file types
        result = (
            f"UNSUPPORTED FILE TYPE:\n"
            f"The extension '{ext}' is not supported by any active agent.\n"
            f"Please provide a .docx, .doc, or .pdf file."
        )
        
    print("-" * 20)
    return result
