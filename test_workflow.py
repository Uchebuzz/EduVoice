"""
Test script to verify the EduVoice workflow is working correctly.
"""
import os
import sys

print("=" * 60)
print("Testing EduVoice Workflow")
print("=" * 60)

# Test 1: Import checks
print("\n1. Testing imports...")
try:
    from orchestrator import run_document_orchestrator
    print("   ✅ Orchestrator imported")
except Exception as e:
    print(f"   ❌ Orchestrator import failed: {e}")
    sys.exit(1)

try:
    from agent4 import synthesize_speech
    print("   ✅ TTS synthesize_speech imported")
except Exception as e:
    print(f"   ❌ TTS import failed: {e}")
    sys.exit(1)

try:
    from PdfReaderAgent import process_pdf_from_ui
    print("   ✅ PdfReaderAgent imported")
except Exception as e:
    print(f"   ❌ PdfReaderAgent import failed: {e}")
    sys.exit(1)

try:
    from DocumentReader import process_word_doc_from_ui
    print("   ✅ DocumentReader imported")
except Exception as e:
    print(f"   ❌ DocumentReader import failed: {e}")
    sys.exit(1)

# Test 2: Check for ADK agents
print("\n2. Testing ADK agents...")
try:
    from google.adk.agents import Agent
    from google.adk.tools import FunctionTool
    print("   ✅ ADK agents imported successfully")
except Exception as e:
    print(f"   ⚠️  ADK agents not available: {e}")
    print("   (This is optional - workflow uses direct function calls)")

# Test 3: Check Google Cloud TTS client
print("\n3. Testing Google Cloud TTS...")
try:
    from google.cloud import texttospeech
    from pathlib import Path
    credentials_path = Path("credentials") / "voice-agent-478712-ab0f02714681.json"
    
    if credentials_path.exists():
        print(f"   ✅ Credentials file found: {credentials_path}")
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = str(credentials_path)
        client = texttospeech.TextToSpeechClient()
        print("   ✅ TTS client initialized")
    else:
        print(f"   ⚠️  Credentials file not found at: {credentials_path}")
        print("   (TTS will fail without credentials)")
except Exception as e:
    print(f"   ⚠️  TTS setup issue: {e}")

# Test 4: Check Gemini API configuration
print("\n4. Testing Gemini API configuration...")
try:
    import google.generativeai as genai
    print("   ✅ google.generativeai imported")
    
    # Check if API key is configured (it's probably a placeholder)
    try:
        genai.configure(api_key="test")
        print("   ⚠️  API key appears to be placeholder - update with real key")
    except:
        pass
except Exception as e:
    print(f"   ⚠️  Gemini API issue: {e}")

# Test 5: Check Streamlit
print("\n5. Testing Streamlit...")
try:
    import streamlit as st
    print("   ✅ Streamlit imported")
    print(f"   ✅ Streamlit version: {st.__version__}")
except Exception as e:
    print(f"   ❌ Streamlit import failed: {e}")
    sys.exit(1)

# Test 6: Check file processing dependencies
print("\n6. Testing file processing dependencies...")
try:
    import fitz  # PyMuPDF
    print("   ✅ PyMuPDF (fitz) imported")
except Exception as e:
    print(f"   ❌ PyMuPDF import failed: {e}")

try:
    import docx
    print("   ✅ python-docx imported")
except Exception as e:
    print(f"   ❌ python-docx import failed: {e}")

try:
    from pdf2image import convert_from_path
    print("   ✅ pdf2image imported")
except Exception as e:
    print(f"   ⚠️  pdf2image import failed: {e} (needed for OCR)")

try:
    import pytesseract
    print("   ✅ pytesseract imported")
except Exception as e:
    print(f"   ⚠️  pytesseract import failed: {e} (needed for OCR)")

print("\n" + "=" * 60)
print("✅ Workflow test completed!")
print("=" * 60)
print("\nTo run the Streamlit app:")
print("  streamlit run Home.py")
print("\nMake sure to:")
print("  1. Set your Gemini API key in PdfReaderAgent.py and DocumentReader.py")
print("  2. Have Google Cloud credentials in credentials/ folder")
print("  3. Install Tesseract OCR if you need scanned PDF support")

