import fitz  # PyMuPDF
import pymupdf4llm
from PIL import Image
import io
import google.generativeai as genai
from pdf2image import convert_from_path
import pytesseract

genai.configure(api_key="YOUR_API_KEY")
vision_model = genai.GenerativeModel("gemini-2.5-flash")
text_model = genai.GenerativeModel("gemini-2.0-flash-lite-preview")


# ==================== Base Agent ====================
class Agent:
    def __init__(self, name):
        self.name = name


# ==================== Sub-Agents ====================
class TextAgent(Agent):
    def summarize_text(self, context_text: str) -> str:
        prompt = f"Provide a brief one-line summary of this:\n{context_text[:2000]}"
        response = text_model.generate_content(prompt)
        return response.text.strip() if response.text else ""


class OcrAgent(Agent):
    def ocr_page(self, pdf_path, page_number):
        print(f"📌 OCR triggered on Page {page_number+1}")
        images = convert_from_path(pdf_path, first_page=page_number+1, last_page=page_number+1)
        text = ""
        for img in images:
            text += pytesseract.image_to_string(img)
        return text.strip()


class VisionAgent(Agent):
    def explain(self, image: Image.Image, context_summary: str) -> str:
        prompt = (
            "Write one concise, natural sentence describing the image. "
            "If it clearly connects to the given summary, "
            "include that meaningfully without explicitly referring to the summary. "
            "If the connection is unclear, only describe what is visually present "
            "without mentioning any mismatch or analysis. "
            "Do not reference the text or summary directly. "
            "Do not explain your reasoning. "
            "Avoid phrases like 'this image shows' or 'the summary says'. "
            f"\n\nSummary (for context): {context_summary}\n"
        )
        resp = vision_model.generate_content([prompt, image])
        return resp.text.strip()



import re

class CleaningAgent:
    def __init__(self):
        self.chapter_pattern = re.compile(r"^#\s+.+")

    def clean(self, text: str) -> str:
        lines = text.split("\n")

        cleaned = []
        buffer_para = []
        chapter_active = False

        for i, line in enumerate(lines):
            stripped = line.strip()

            # Detect new chapter
            if self.chapter_pattern.match(stripped):
                # close previous chapter cleanly
                if chapter_active:
                    cleaned.append("\n--- END OF CHAPTER ---\n")
                chapter_active = True
                cleaned.append("\n" + stripped + "\n")
                continue

            # Normal paragraph line
            if stripped:
                buffer_para.append(stripped)
            else:
                if buffer_para:
                    cleaned.append(" ".join(buffer_para))
                    buffer_para = []

        # flush last paragraph
        if buffer_para:
            cleaned.append(" ".join(buffer_para))

        # Append final chapter end
        cleaned.append("\n--- END OF CHAPTER ---\n")

        return "\n".join(cleaned)



# ==================== Main PDF Reader Agent ====================
class PdfReaderAgent(Agent):
    def __init__(self):
        super().__init__("PdfReaderAgent")
        self.text_agent = TextAgent("TextAgent")
        self.ocr_agent = OcrAgent("OcrAgent")
        self.vision_agent = VisionAgent("VisionAgent")

    def get_best_context(self, idx, summaries):
        if summaries[idx]: return summaries[idx]
        if idx > 0 and summaries[idx-1]: return summaries[idx-1]
        if idx < len(summaries)-1 and summaries[idx+1]: return summaries[idx+1]
        return "No readable text in nearby pages."

    def process_pdf(self, pdf_path):
        doc = fitz.open(pdf_path)
        enhanced = pymupdf4llm.to_markdown(doc, page_chunks=True, write_images=False)

        all_summaries = []
        raw_text = []

        # ---------- PASS 1: Text + OCR ----------
        for idx, chunk in enumerate(enhanced):
            text = chunk.get("text", "").strip()
            images = chunk.get("images", [])

            if not text:  # No text found
                    text = self.ocr_agent.ocr_page(pdf_path, idx)

            chunk["text"] = text  # Update chunk

            summary = self.text_agent.summarize_text(text) if text else None
            all_summaries.append(summary)

        # ---------- PASS 2: Writing & Vision ----------
        
        for idx, chunk in enumerate(enhanced):
            print(f"\n--- Page {idx+1} ---")
            text = chunk.get("text", "").strip()
            images = chunk.get("images", [])
            img_explanation = None

            if images:
                meta = images[0]
                bbox = meta["bbox"]
                page = doc[idx]
                pix = page.get_pixmap(clip=bbox, dpi=200)
                img = Image.open(io.BytesIO(pix.tobytes()))
                context = self.get_best_context(idx, all_summaries)
                img_explanation = self.vision_agent.explain(img, context)
                print("🖼️ Explained:", img_explanation)

            if text:
             raw_text.append(text)

            if img_explanation:
             raw_text.append(f"\n--- EXPLAINING IMAGE ---\n {img_explanation} --- CONTINUING WITH TEXT ---\n")


        combined = "\n".join(raw_text)

        cleaner = CleaningAgent()
        cleaned_output = cleaner.clean(combined)
        print("🎉 Cleaning + Structuring complete!)
        return cleaned_output
        


                


# ==================== Runner ====================
if __name__ == "__main__":
    agent = PdfReaderAgent()
    agent.process_pdf("story-book.pdf")
