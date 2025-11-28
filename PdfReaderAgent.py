import fitz
import pymupdf4llm
from PIL import Image
import io
from pdf2image import convert_from_path
import pytesseract
import re
import google.generativeai as genai

from google.adk.agents import Agent
from google.adk.tools import FunctionTool 

# ==================== 1. Configure Gemini & Models ====================

genai.configure(api_key="AIzaSyDk4u-4y2-7RcibtnNIitehuxLgiMynGnc")
vision_model = genai.GenerativeModel("gemini-2.5-flash")
text_model = genai.GenerativeModel("gemini-2.0-flash-lite-preview")


class PdfReaderAgent(Agent):


# ==================== 2. Tools (Original Python Functions) ====================
    def summarize_text_tool(self ,context_text: str) -> str:
        """Uses the text model to provide a brief one-line summary of the text."""
        prompt = f"Provide a brief one-line summary of this:\n{context_text}"
        resp = text_model.generate_content(prompt)
        return resp.text.strip() if resp.text else ""

    def ocr_page_tool(self, pdf_path: str, page_number: int) -> str:
        """Performs Optical Character Recognition (OCR) on a specific PDF page."""
        print("--Running OCR--")
        images = convert_from_path(pdf_path, first_page=page_number+1, last_page=page_number+1)
        text = ""
        for img in images:
            text += pytesseract.image_to_string(img)
        return text.strip()

    def explain_image_tool(self, image_bytes: bytes, context_summary: str) -> str:
        """Uses the vision model to describe an image, connecting it to context."""
        print("Image explaination tool running...")
        img = Image.open(io.BytesIO(image_bytes))
        prompt = (
            "Write one concise, natural sentence describing the image. "
            "If it clearly connects to the given summary, include that meaningfully. "
            "Only describe what is visually present. Do not reference the text or summary directly. "
            f"\n\nSummary (for context): {context_summary}\n"
        )
        resp = vision_model.generate_content([prompt, img])
        return resp.text.strip()

    def clean_text_tool(self ,raw_text: str) -> str:
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
                if chapter_active:
                    cleaned.append("\n--- END OF CHAPTER ---\n")
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
        cleaned.append("\n--- END OF CHAPTER ---\n")
        return "\n".join(cleaned)
    
    

    def __init__(self):
        summarize_tool_adk = FunctionTool(self.summarize_text_tool)
        ocr_tool_adk = FunctionTool(self.ocr_page_tool)
        explain_tool_adk = FunctionTool(self.explain_image_tool)
        clean_tool_adk = FunctionTool(self.clean_text_tool)
        super().__init__(
            name="PdfReaderAgent",
            model="gemini-2.0-flash-lite-preview",
            instruction="""
            You are a PDF Reader Agent. Your task is to process chunked PDF content:
            1. Assess text; use OCR if text is sparse.
            2. Summarize the text using the 'summarize_text_tool'.
            3. If an image is present, explain it using the 'explain_image_tool' in the context of the summary.
            4. Return the combined, summarized, and explained text.
            5. The final output must be cleaned using 'clean_text_tool'.
            """,
            tools=[summarize_tool_adk, ocr_tool_adk, explain_tool_adk, clean_tool_adk],
            output_key="pdf_processing_results"
        )  
        pass

    # ==================== 5. Runner Function ====================
    def process_pdf(self,pdf_path: str) -> str:
        """
        Manually orchestrates the PDF processing workflow using the defined functions.
        This avoids the 'FunctionTool' object is not callable error by calling 
        the underlying Python functions directly.
        """

        print(f"Starting extraction for {pdf_path}...")

        doc = fitz.open(pdf_path)
        enhanced = pymupdf4llm.to_markdown(doc, page_chunks=True, write_images=False)

        all_summaries = []
        raw_text = []

        # ---------- PASS 1: Text Extraction & Summarization ----------
        for idx, chunk in enumerate(enhanced):
            
            text = chunk.get("text", "").strip()
            
            if not text:
                text = self.ocr_page_tool(pdf_path, idx)
            
            chunk["text"] = text
            
        
            summary = self.summarize_text_tool(text) if text else None
            all_summaries.append(summary)


        # ---------- PASS 2: Image Explanation & Combine ----------
        for idx, chunk in enumerate(enhanced):
            text = chunk.get("text", "").strip()
            images = chunk.get("images", [])
            img_explanation = None

            if images:
                # Get the first image's metadata and clip the image bytes
                meta = images[0]
                bbox = meta["bbox"]
                page = doc[idx]
                pix = page.get_pixmap(clip=bbox, dpi=200)
                img_bytes = io.BytesIO(pix.tobytes()).getvalue()
                
                # Determine context (current page summary or previous page summary)
                context = all_summaries[idx] or (all_summaries[idx-1] if idx > 0 else "")
                
                # FIX: Call the explain_image_tool
                img_explanation = self.explain_image_tool(img_bytes, context)

            if text:
                raw_text.append(f"\n {text} \n")
            if img_explanation:
                raw_text.append(f"\n\n--- EXPLAINING IMAGE ---\n\n{img_explanation}\n\n")

        # ---------- PASS 3: Cleaning ----------
        combined = "\n".join(raw_text)
        # FIX: Call the clean_text_tool
        cleaned_output = self.clean_text_tool(combined)

        print("\n" + "="*50)
        print("✅ PDF processed successfully!")
        print("="*50)

        return cleaned_output
            
            