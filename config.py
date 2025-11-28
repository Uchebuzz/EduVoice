import os
from dotenv import load_dotenv

load_dotenv()  # loads .env

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
