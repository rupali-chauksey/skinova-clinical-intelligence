import re
import os
from pathlib import Path
from dotenv import load_dotenv
from deepgram import DeepgramClient

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent
DEFAULT_DOCTOR_AUDIO = BASE_DIR / "doctor_response.mp3"


def convert_text_to_doctor_audio(
    text,
    output_filepath=DEFAULT_DOCTOR_AUDIO
):
    deepgram_api_key = os.environ.get("DEEPGRAM_API_KEY")

    if not deepgram_api_key:
        raise ValueError("Missing DEEPGRAM_API_KEY")

    # Remove <think>...</think> from AI response
    text = re.sub(
        r"<think>.*?</think>",
        "",
        text,
        flags=re.DOTALL
    ).strip()

    # Deepgram allows maximum 2000 characters
    text = text[:1800]

    deepgram = DeepgramClient(api_key=deepgram_api_key)

    audio = deepgram.speak.v1.audio.generate(
        text=text,
        model=os.environ.get(
            "DEEPGRAM_TTS_MODEL",
            "aura-2-thalia-en"
        ),
        encoding="mp3",
    )

    output_filepath = Path(output_filepath)

    with output_filepath.open("wb") as file:
        for chunk in audio:
            file.write(chunk)

    return output_filepath