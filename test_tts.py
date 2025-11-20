"""
Simple test script for Google Cloud Text-to-Speech API
"""
import os
from pathlib import Path
from google.cloud import texttospeech

# Set up credentials
CREDENTIALS_PATH = Path(__file__).parent / "credentials" / "voice-agent-478712-ab0f02714681.json"

if not CREDENTIALS_PATH.exists():
    print(f"❌ Error: Credentials file not found at {CREDENTIALS_PATH}")
    exit(1)

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = str(CREDENTIALS_PATH)
print(f"✓ Credentials file found: {CREDENTIALS_PATH}")

# Initialize client
try:
    client = texttospeech.TextToSpeechClient()
    print("✓ Text-to-Speech client initialized successfully")
except Exception as e:
    print(f"❌ Error initializing client: {e}")
    exit(1)

# Test synthesis
try:
    print("\n📢 Testing speech synthesis...")
    
    # Configure the synthesis
    synthesis_input = texttospeech.SynthesisInput(
        text="Hello! This is a test of the Google Cloud Text-to-Speech API for EduVoice."
    )
    
    voice = texttospeech.VoiceSelectionParams(
        language_code="en-US",
        ssml_gender=texttospeech.SsmlVoiceGender.NEUTRAL
    )
    
    audio_config = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.MP3
    )
    
    # Perform the synthesis
    response = client.synthesize_speech(
        input=synthesis_input,
        voice=voice,
        audio_config=audio_config
    )
    
    # Save the audio to a file
    output_file = "test_output.mp3"
    with open(output_file, "wb") as out:
        out.write(response.audio_content)
    
    print(f"✓ Audio synthesized successfully!")
    print(f"✓ Output saved to: {output_file}")
    print(f"✓ Audio size: {len(response.audio_content)} bytes")
    print("\n🎉 All tests passed! Your Google Text-to-Speech API is working correctly.")
    
except Exception as e:
    print(f"❌ Error during synthesis: {e}")
    exit(1)

