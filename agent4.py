import os
from pathlib import Path
from typing import Optional

from google.cloud import texttospeech

# Optional imports for agent functionality (only needed when running agent4.py directly)
try:
    from google.assistant.agents import Agent
    from google.assistant.context import Context
    from google.assistant.skill import Skill
    ASSISTANT_SDK_AVAILABLE = True
except ImportError:
    # Assistant SDK not available - agent functionality will be skipped
    ASSISTANT_SDK_AVAILABLE = False
    Agent = None
    Context = None
    Skill = None

# Set up Google Cloud credentials
CREDENTIALS_PATH = Path(__file__).parent / "credentials" / "voice-agent-478712-ab0f02714681.json"
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = str(CREDENTIALS_PATH)

# Initialize the Text-to-Speech client
client = texttospeech.TextToSpeechClient()


def synthesize_speech(
    text: str,
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

    synthesis_input = texttospeech.SynthesisInput(text=text)

    voice = texttospeech.VoiceSelectionParams(
        language_code=language,
        ssml_gender=voice_gender,
    )

    audio_config = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.MP3,
    )

    response = client.synthesize_speech(
        input=synthesis_input,
        voice=voice,
        audio_config=audio_config,
    )

    return response.audio_content


# Agent functionality - only available if Assistant SDK is installed
if ASSISTANT_SDK_AVAILABLE and Skill and Agent:
    class Agent4Skill(Skill):
        """Skill that exposes a `speak_text` intent using Google Cloud TTS."""

        def __init__(self) -> None:
            super().__init__(name="Agent 4", description="Google TTS voice agent")

        @Skill.intent("speak_text")
        async def speak_out(self, context: Context) -> Context:
            """Handle the `speak_text` intent."""

            text_speak: Optional[str] = context.slot("text_speak")
            voice_gender: str = context.slot("voice_gender") or "NEUTRAL"
            language_code: str = context.slot("language_code") or "en-US"

            if not text_speak:
                await context.speak("I didn't receive any text to speak.")
                return context.done()

            audio_content = synthesize_speech(
                text=text_speak,
                gender=voice_gender,
                language=language_code,
            )

            await context.speak_audio(audio_content)

            return context.done()


    agent = Agent(
        name="Agent 4",
        description="Google TTS voice agent using Cloud Text-to-Speech.",
        skills=[Agent4Skill()],
    )

    if __name__ == "__main__":
        agent.run()
else:
    # Assistant SDK not available - agent functionality skipped
    agent = None
    
    if __name__ == "__main__":
        print("⚠️ Google Assistant SDK not available. Install google-assistant-sdk to use agent functionality.")
        print("   The synthesize_speech function is still available for direct use.")