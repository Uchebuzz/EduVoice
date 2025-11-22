import fitz  # PyMuPDF
import pymupdf4llm
from PIL import Image
import io
import google.generativeai as genai
import fitz

# Configure your model

genai.configure(api_key="your api key")

#used diff models as they have some limits
model = genai.GenerativeModel("gemini-2.5-flash") 
model2= genai.GenerativeModel('gemini-2.0-flash-lite-preview')


def summarize_text(context_text: str) -> str:
    prompt = f"Provide a brief one-line summary of the following text:\n\"\"\"\n{context_text}\n\"\"\""
    resp = model2.generate_content(prompt)
    return resp.text.strip()



def get_best_context(idx, summaries):
    if summaries[idx] is not None and summaries[idx].strip():
        return summaries[idx]

    # Try previous page context
    if idx > 0 and summaries[idx - 1]:
        return summaries[idx - 1]

    # Try next page context
    if idx < len(summaries) - 1 and summaries[idx + 1]:
        return summaries[idx + 1]

    return "No readable text in nearby pages."


def explain_image_with_context(image: Image.Image, context_summary: str) -> str:
    prompt = f"""
Text-context of the page:
\"\"\"{context_summary}\"\"\"

Now, explain how this image connects with the given text in **one sentence and please match the tone with the context**.
"""
    # 🚫 No need for base64 conversion
    resp = model.generate_content(
        [
            prompt,
            image
        ]
    )
    return resp.text.strip()


def process_pdf(pdf_path: str):

    doc = fitz.open(pdf_path)
    enhanced = pymupdf4llm.to_markdown(doc, page_chunks=True, write_images=False)
    print(f"Total pages: {len(enhanced)}")

    # Save all text summaries first
    all_summaries = []

    for idx, chunk in enumerate(enhanced):
        text = chunk.get("text", "").strip()
        if text:
                summary = summarize_text(text)
                all_summaries.append(summary)
        else:
                all_summaries.append(None)

    # Second pass for images and write to file
    with open("output.txt", "w") as file:
        for idx, chunk in enumerate(enhanced):
            print(f"\n--- Page {idx+1} ---")
            images = chunk.get("images", [])
            text = chunk.get("text", "").strip()
            file.write(text)
                
            if not images:
                continue

            img_meta = images[0]
            bbox = img_meta["bbox"]

            page = doc[idx]
            pix = page.get_pixmap(clip=bbox, dpi=200)
            img = Image.open(io.BytesIO(pix.tobytes()))
            img.show()

                # Smart context retrieval
            context = get_best_context(idx, all_summaries)

            explanation = explain_image_with_context(img, context)
            file.write("\n --- explaining image \n---" + explanation)
            print("🖼️ Image Explanation:", explanation)




if __name__ == "__main__":
 process_pdf("story-book.pdf")
