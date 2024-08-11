import os
import random
import subprocess
import requests
from pathlib import Path
import argparse


ELEVEN_LABS_API_KEY = "sk_f8af6014f4721cf708d801da3c16e05000e90e938e37c898"


def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Generate a voice baseline using elevenlabs.io API."
    )
    parser.add_argument(
        "--voice_name", type=str, required=True, help="Your custom name for this voice"
    )
    parser.add_argument(
        "--voice_id",
        type=str,
        required=True,
        help="ID of the voice from the elevenlabs 'Voices' page, such as 'FmJ4FDkdrYIKzBTruTkV'",
    )
    return parser.parse_args()


def generate_voice_baseline(voice_name: str, voice_id: str) -> None:
    # A high-quality alternative to finding, recording, and editing your own voices.
    #
    # Uses elevenlabs.io API to generate sample audio files in .wav format which can serve
    # as the baseline for the local text-to-speech voice cloning process used in `generate_voice_pack.py`

    # 500 characters of GPT-4o generated alliterative text with phonetic variety
    text_samples = [
        "Astonishing Aston Martins accelerate at amazing angles.",
        "Blazing Bugattis blast by barriers.",
        "Charging Chevrolets chase championship challenges.",
        "Daring drivers dominate double drifts.",
        "Enthusiastic engines echo exhilarating excitement.",
        "Fearless Ferraris fly fast and fierce.",
        "Glorious gears glide.",
        "High-speed Hondas hit hairpin corners.",
        "Incredible IndyCars ignite intense interest.",
        "Jumping Jaguars jostle for joyful jousts.",
        "Kinetic Kias keep kicking karma.",
        "Lightning Lamborghinis leap large loops.",
    ]

    output_dir = f"output/baseline/{voice_name}"

    for text_sample_idx, text_sample in enumerate(text_samples, 1):
        # create and download the audio file (.mp3) via Eleven Labs API
        generate_speech_elevenlabs(
            text=text_sample,
            voice_name=voice_name,
            voice_id=voice_id,
            output_dir=output_dir,
            output_filename=f"{text_sample_idx}",
        )

        # convert the audio file to .wav and trim silence from start and end
        prefix = f"{output_dir}/{text_sample_idx}"
        mp3_filename = f"{prefix}.mp3"
        untrimmed_wav_filename = f"{prefix}_raw.wav"
        trimmed_wav_filename = f"{prefix}.wav"

        convert_mp3_to_wav(mp3_filename, untrimmed_wav_filename)
        trim_silence(untrimmed_wav_filename, trimmed_wav_filename)

        # clean up interim files
        remove_file(mp3_filename)
        remove_file(untrimmed_wav_filename)

        print(f"Generated {trimmed_wav_filename}")

    print(f"Voice baseline generation complete for {voice_name} in {output_dir}")


def generate_speech_elevenlabs(
    text: str, voice_name: str, voice_id: str, output_dir: str, output_filename: str
) -> None:
    """
    Eleven labs API returns mp3 format data
    """

    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"

    payload = {
        "text": text,
        "model_id": "eleven_multilingual_v2",  # from GET /v1/models
        "voice_settings": {
            "stability": 0.5,
            "similarity_boost": 0.5,
            "style": 0.6,
            "use_speaker_boost": True,
        },
        "seed": random.randrange(1, 9999999),
    }
    headers = {
        "Content-Type": "application/json",
        "xi-api-key": ELEVEN_LABS_API_KEY,
    }

    response = requests.request("POST", url, json=payload, headers=headers)

    if response.status_code == 200:
        # if needed, create output directory
        Path(output_dir).mkdir(parents=True, exist_ok=True)

        full_output_filename = f"{output_dir}/{output_filename}.mp3"
        with open(full_output_filename, "wb") as f:
            for chunk in response.iter_content(chunk_size=1024):
                if chunk:
                    f.write(chunk)
    else:
        print(f"Error from Eleven Labs API: {response.status_code} - {response.text}")


def convert_mp3_to_wav(input_file: str, output_file: str) -> None:
    """
    Simple CLI conversion of mp3 to wav, requires ffmpeg
    """
    ffmpeg_command: list[str] = ["ffmpeg", "-y", "-i", input_file, output_file]

    try:
        subprocess.run(ffmpeg_command, check=True)
    except subprocess.CalledProcessError as e:
        print(f"An error occurred: {e}")


def trim_silence(input_file: str, output_file: str) -> None:
    """
    Trim silence from both sides of file, requires sox
    """
    sox_command: list[str] = [
        "sox",
        "-V1",
        "-q",
        input_file,
        output_file,
        "silence",
        "1",
        "0.1",
        "0.1%",
        "reverse",
        "silence",
        "1",
        "0.1",
        "0.3%",
        "reverse",
        "norm",
    ]

    try:
        subprocess.run(sox_command, check=True)
    except subprocess.CalledProcessError as e:
        print(f"An error occurred: {e}")


def remove_file(file_path: str) -> None:
    """
    Remove the file at the specified path.
    """
    path = Path(file_path)
    path.unlink()


if __name__ == "__main__":
    args = parse_arguments()
    print("Generating voice baseline using Eleven Labs API...")
    generate_voice_baseline(args.voice_name, args.voice_id)
