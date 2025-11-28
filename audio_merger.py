#pydub needs fmpeg to be installed in the OS
from pydub import AudioSegment


def merge_audio_files(audio_chunks: list, output_path: str, add_silence_ms: int = 300):
    """
    Merges multiple audio chunks into a single audio file.
    - audio_chunks: list of file paths in correct order
    - add_silence_ms: silence between chunks (default: 0.3 sec)
    """

    if not audio_chunks:
        raise ValueError("No audio chunks provided")

    final_audio = AudioSegment.silent(duration=0)

    silence = AudioSegment.silent(duration=add_silence_ms)

    print("Files passed to merger: ")

    for chunk_path in audio_chunks:
        segment = AudioSegment.from_file(chunk_path)
        final_audio += segment + silence

    final_audio.export(output_path, format=output_path.split(".")[-1])

    return output_path
