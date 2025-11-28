
from PdfReaderAgent import PdfReaderAgent
from DocumentReaderAgent import DocumentReaderAgent

import google.generativeai as genai

genai.configure(api_key="API_KEY")
text_model = genai.GenerativeModel("gemini-2.0-flash-lite-preview")

class Orchestrator:
    def __init__(self):
        self.pdf_agent = PdfReaderAgent()
        self.doc_agent = DocumentReaderAgent()
        # Add other agents here when needed

    def route_task(self, file_path: str) -> str:
        """
        Decide which agent(s) should process the file using LLM reasoning.
        """
        # Compose a prompt for the LLM
        prompt = f"""
        You are an AI orchestrator.
        File path: {file_path}

        Decide which agent is most suitable to process this file based on extension.
        Respond with only the agent name (e.g., 'PdfReaderAgent','DocumentReaderAgent').
        """

        response = text_model.generate_content(prompt)
      

        chosen_agent = response.text.strip()
        print(chosen_agent)

        # Dynamic routing
        if chosen_agent == "PdfReaderAgent":
            return self.pdf_agent.process_pdf(file_path)
        elif chosen_agent == "DocumentReaderAgent":
            return self.doc_agent.process_word_doc(file_path)
        else:
            return f"No suitable agent found for the file.."
