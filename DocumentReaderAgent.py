import docx
import zipfile
import os
import io
import base64
import re
from PIL import Image
from typing import List, Dict, Any, Union

import google.generativeai as genai
from google.adk.agents import Agent
from google.adk.tools import FunctionTool

# ==================== 1. Configure Gemini & Models ====================

genai.configure(api_key="API_KEY")
vision_model = genai.GenerativeModel("gemini-2.5-flash")
text_model = genai.GenerativeModel("gemini-2.0-flash-lite")

# ==================== 2. Helper Functions (Image Handling) ====================

class DocumentReaderAgent (Agent):


    def extract_all_images_to_base64(self, doc_path: str) -> Dict[str, str]:
        """
        Extracts all images from a DOCX file (zip archive) and returns them
        as a dictionary mapping the image part name (e.g., 'image1.jpeg') to its base64 string.
        """
        images = {}
        try:
            # DOCX is a zip file, images are in 'word/media/'
            with zipfile.ZipFile(doc_path, 'r') as docx_zip:
                media_files = [name for name in docx_zip.namelist() if name.startswith('word/media/')]
                
                for media_file in media_files:
                    if not os.path.basename(media_file).startswith('.'):
                        with docx_zip.open(media_file) as image_file:
                            image_bytes = image_file.read()
                            base64_img = base64.b64encode(image_bytes).decode('utf-8')
                            images[os.path.basename(media_file)] = base64_img
        except Exception as e:
            print(f"Warning: Could not extract all images from DOCX. Details: {e}")
            
        return images

    # ==================== 3. Tool Functions ====================

    def extract_text_and_images_tool(self, doc_path: str) -> tuple[List[Dict[str, Union[str, List[str]]]], Dict[str, str]]:
        """
        Extracts text from a DOCX file, identifies image references within paragraphs,
        and returns a list of text chunks plus a dictionary of all image base64 data.
        """
        # This is the line that throws PackageNotFoundError if the file is not found/valid:
        doc = docx.Document(doc_path)
        all_images_data = self.extract_all_images_to_base64(doc_path) 
        
        chunks = []
        
        for paragraph in doc.paragraphs:
            text = paragraph.text
            style_name = paragraph.style.name if paragraph.style else "Normal"
            
            # Check XML for image data reference (using a heuristic for simplicity)
            has_image = 'graphicData' in paragraph._p.xml
            
            chunk = {
                "text": text.strip(),
                "style": style_name,
                "image_references": []
            }
            
            if has_image and all_images_data:
                # Assign ALL extracted image names to the chunk that contains an image marker
                chunk["image_references"] = list(all_images_data.keys())
                
            chunks.append(chunk)

        return chunks, all_images_data

    def summarize_text_tool(self, context_text: str) -> str:
        """Uses the text model to provide a brief one-line summary of the text."""
        if not context_text:
            return ""
        prompt = f"Provide a brief one-line summary of this:\n{context_text[:2000]}"
        resp = text_model.generate_content(prompt)
        return resp.text.strip() if resp.text else ""

    def explain_image_tool(self, image_base64: str, context_summary: str) -> str:
        """Uses the vision model to describe a base64 encoded image, connecting it to context."""
        if not image_base64:
            return "No image data provided for explanation."
            
        try:
            image_bytes = base64.b64decode(image_base64)
        except:
            return "Error: Could not decode image data."
            
        img = Image.open(io.BytesIO(image_bytes))
        prompt = (
            "Write one concise, natural sentence describing the image. "
            "Use the summary for context but do not reference the text or summary directly. "
            f"\n\nSummary (for context): {context_summary}\n"
        )
        resp = vision_model.generate_content([prompt, img])
        return resp.text.strip()

    def clean_text_tool(self, raw_text: str) -> str:
        """Cleans up raw text, structuring it with paragraphs and chapter breaks."""
        
        chapter_pattern = re.compile(r"^#\s+.+")
        lines = raw_text.split("\n")
        cleaned = []
        buffer_para = []
        chapter_active = False

        print("cleaning raw text...")

        for line in lines:
            stripped = line.strip()
            if chapter_pattern.match(stripped):
                if buffer_para:
                    cleaned.append(" ".join(buffer_para))
                    buffer_para = []
                if chapter_active:
                    cleaned.append("\n--- END OF SECTION ---\n")
                chapter_active = True
                cleaned.append("\n" + stripped + "\n")
                continue
            if stripped:
                buffer_para.append(stripped)
            else:
                if buffer_para:
                    cleaned.append(" ".join(buffer_para))
                    buffer_para = []
        if buffer_para:
            cleaned.append(" ".join(buffer_para))
        if chapter_active:
            cleaned.append("\n--- END OF SECTION ---\n")
        return "\n".join(cleaned)

    
    def __init__(self):
        extract_doc_tool_adk = FunctionTool(self.extract_text_and_images_tool)
        summarize_doc_tool_adk = FunctionTool(self.summarize_text_tool)
        explain_image_doc_tool_adk = FunctionTool(self.explain_image_tool)
        clean_doc_tool_adk = FunctionTool(self.clean_text_tool)
        super().__init__(
            name="WordDocReaderAgent",
            model="gemini-2.0-flash-lite-preview",
            instruction="""
            You are a Word Document Extraction Agent. Your task is to process the document content.
            1. **Extract:** Use the 'extract_text_and_images_tool' to get text chunks and image references.
            2. **Process:** For each chunk: summarize the text, and if image references exist, use the 'explain_image_tool' with the corresponding base64 image data and the summary for context.
            3. **Combine:** Combine all original text, summaries, and image explanations sequentially.
            4. **Clean:** Finally, use the 'clean_text_tool' on the entire combined output.
            """,
            tools=[
                extract_doc_tool_adk, 
                summarize_doc_tool_adk, 
                explain_image_doc_tool_adk, 
                clean_doc_tool_adk
            ],
            output_key="cleaned_doc_content")
        pass

    def process_word_doc(self, doc_path: str) -> str:
        """
        Manually orchestrates the Word document processing workflow, including images.
        """
        print(f"Starting extraction for {doc_path}...")
        
        # 1. Extraction: Get all chunks and all image data
    
        all_chunks, all_images_data = self.extract_text_and_images_tool(doc_path)

        combined_raw_text = []
        
        # 2. Iterate and process each chunk 
        for idx, chunk in enumerate(all_chunks):
            text = chunk["text"].strip()
            
            heading_marker = f"# {chunk['style']}:" if chunk['style'].startswith('Heading') else ""
            
            # Get text summary
            summary = self.summarize_text_tool(text)
            
            # Start the chunk output
            combined_raw_text.append(f"\n{heading_marker}")
        
            
            # Process images associated with this chunk
            if chunk["image_references"]:
                # Use the first image reference 
                image_name = chunk["image_references"][0]
                if image_name in all_images_data:
                    image_base64 = all_images_data[image_name]
                    
                    # Explain the image using the text summary as context
                    img_explanation = self.explain_image_tool(image_base64, summary)
                    combined_raw_text.append(f"\n\nImage Explanation : {img_explanation}\n\n")
            
            # Append the full text of the paragraph/section
            if text:
                combined_raw_text.append(text)
            
        
        # 3. Clean the combined output
        full_raw_text = "\n".join(combined_raw_text)

        print("raw text extraction done...")

        # Clean the output
        cleaned_output = self.clean_text_tool(full_raw_text)

        print("\n" + "="*50)
        print("✅ Document processed successfully!")
        print("="*50)
        
        return cleaned_output
