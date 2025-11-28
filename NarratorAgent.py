import os
from pathlib import Path
from audio_merger import merge_audio_files

from google.cloud import texttospeech
from google.adk.agents import Agent
from google.adk.tools import FunctionTool


# Set up Google Cloud credentials
CREDENTIALS_PATH = Path(__file__).parent / "credentials" / "voice-agent-478712-ab0f02714681.json"
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = str(CREDENTIALS_PATH)

# Initialize the Text-to-Speech client
client = texttospeech.TextToSpeechClient()

class NarratorAgent(Agent):

    def synthesize_speech(self,
        chunks: list[str],
        gender: str = "NEUTRAL",
        language: str = "en-US",
    ) -> bytes:
        """
        Google Cloud Text-to-Speech helper.

        :param text: Text to synthesize.
        :param gender: One of "MALE", "FEMALE", or "NEUTRAL".
        :param language: BCP-47 language code, e.g. "en-US", "en-GB", "en-NG", "fr-FR".
        :return: Raw MP3 audio bytes.
        """

        # Convert gender text → Google enum
        gender_map = {
        "MALE": texttospeech.SsmlVoiceGender.MALE,
        "FEMALE": texttospeech.SsmlVoiceGender.FEMALE,
        "NEUTRAL": texttospeech.SsmlVoiceGender.NEUTRAL,
       }

        voice_gender = gender_map.get(
            gender.upper(),
            texttospeech.SsmlVoiceGender.NEUTRAL,
        )

        voice = texttospeech.VoiceSelectionParams(
            language_code=language,
            ssml_gender=voice_gender,
        )

        audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.MP3,
        )

        audio_files = []

        for i, text in enumerate(chunks):
            # print(text)
            print(f"Generating audio for chunk {i+1}/{len(chunks)}")

            synthesis_input = texttospeech.SynthesisInput(text=text)

            response = client.synthesize_speech(
            input = synthesis_input,
            voice= voice,
            audio_config= audio_config)

            audio = response.audio_content
            file_path = f"audio_chunk_{i+1}.mp3"

            with open(file_path, "wb") as f:
                f.write(audio)
            
            audio_files.append(file_path)

        # Merge into 1 file
        final_audio = merge_audio_files(audio_files, "final_story.mp3")

        return final_audio


   
    def __init__(self):
        synthesize_speech_tool= FunctionTool(self.synthesize_speech)
        super().__init__(  
            name="NarratorAgent",
            model="gemini-2.5-flash",
            instruction="""
            You are a direct Text-to-Speech (TTS) executor. 
            You ahve to call 'synthesize_speech_tool' with the provided text chunks to convert it to speech"
            """,
            tools=[
                synthesize_speech_tool
            ],
            output_key="generated_audio")
        pass