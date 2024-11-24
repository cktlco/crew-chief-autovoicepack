# Usage example
# python record_elevenlabs_voice.py --eleven_labs_api_key XXXXX --voice_id aTTiK3YzK3dXETpuDE2h --voice_name Leon_de --language de

import os
import random
import subprocess
import requests
from pathlib import Path
import argparse


def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Generate a voice baseline using elevenlabs.io API."
    )
    parser.add_argument(
        "--eleven_labs_api_key", type=str, required=True, help="Eleven Labs API key"
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
    parser.add_argument(
        "--language",
        type=str,
        default="en",
        help="Language code, to choose the input phrases",
    )
    return parser.parse_args()


def generate_voice_baseline(
    eleven_labs_api_key: str, voice_name: str, voice_id: str, language: str = "en"
) -> None:
    # A high-quality alternative to finding, recording, and editing your own voices.
    #
    # Uses elevenlabs.io API to generate sample audio files in .wav format which can serve
    # as the baseline for the local text-to-speech voice cloning process used in `generate_voice_pack.py`

    # 500 characters of GPT-4o generated alliterative text with phonetic variety
    text_samples_en = [
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
    text_samples_de = [
        "Atemberaubende Audi beschleunigen an atemberaubenden Ansätzen.",
        "Blitzschnelle BMWs brausen an Barrikaden vorbei.",
        "Champagner-Chevrolets kämpfen gegen herausfordernde Rennen.",
        "Dynamische Dacias dominieren enge Drehungen.",
        "Energiegeladene Engines erzeugen aufregende Aufregung.",
        "Furchtlose Ferraris fliegen schnell und stark.",
        "Glorreiche Getriebe gleiten geschmeidig.",
        "Hochgeschwindigkeits-Hondas halten Haarnadelkurven.",
        "Incredible IndyCars entfachen intensives Interesse.",
        "Sprunghafte Jaguars kämpfen um freudige Duelle.",
        "Kinetische Kias kicken konsequent weiter.",
        "Blitzschnelle Lamborghinis springen große Schleifen.",
    ]
    text_samples_it = [
        "Audaci Audi accelerano ad angoli straordinari.",
        "Blitzante Bugatti battagliano oltre barriere.",
        "Coraggiosi Chevrolet cercano campionati sfidanti.",
        "Determinati driver dominano doppi derapaggi.",
        "Entusiasti motori echeggiano emozionanti eccitazioni.",
        "Fearless Ferrari volano veloci e vigorosi.",
        "Gloriosi ingranaggi scivolano fluidamente.",
        "Honda ad alta velocità affrontano curve a gomito.",
        "Incredibili IndyCars accendono intenso interesse.",
        "Giocate Jaguars gareggiano per gioiose duelli.",
        "Kinetic Kia continuano a calciare il karma.",
        "Lampo Lamborghini saltano grandi loop.",
    ]
    text_samples_es = [
        "Asombrosos Audis aceleran en ángulos asombrosos.",
        "Brillantes Bugatti pasan barreras rápidamente.",
        "Chevrolet cargadas cazan desafíos de campeonato.",
        "Valientes conductores dominan dobles derrapes.",
        "Entusiastas motores resuenan excitante emoción.",
        "Feroces Ferraris vuelan rápidos y fieros.",
        "Gloriosas transmisiones deslizándose suavemente.",
        "Hondas de alta velocidad enfrentan curvas cerradas.",
        "Increíbles IndyCars encienden intenso interés.",
        "Juguetones Jaguars compiten en justas alegres.",
        "Kias cinéticas siguen pateando el karma.",
        "Lamborghinis relampagueantes saltan grandes lazos.",
    ]
    text_samples_cs = [
        "Astonishing Audi akcelerují na úžasných úhlech.",
        "Bleskoví Bugatti protínají bariéry.",
        "Chevrolet nabité honí šampionátní výzvy.",
        "Odvážní řidiči dominují dvojitým driftům.",
        "Nadšené motory ozývají vzrušující vzrušení.",
        "Nebojácí Ferrari létají rychle a divoce.",
        "Slavné převodovky kloužou hladce.",
        "Vysokorychlostní Hondy zvládají úzké zatáčky.",
        "Neuvěřitelné IndyCars zapalují intenzivní zájem.",
        "Skákající Jaguary soupeří o radostné souboje.",
        "Kinetická Kia stále kopou karmu.",
        "Bleskoví Lamborghini skáčou velké smyčky.",
    ]

    # choose the text samples based on the requested language
    text_samples = {
        "en": text_samples_en,
        "de": text_samples_de,
        "it": text_samples_it,
        "es": text_samples_es,
        "cs": text_samples_cs,
    }[language]

    output_dir = f"baseline/{voice_name}"

    for text_sample_idx, text_sample in enumerate(text_samples, 1):
        # create and download the audio file (.mp3) via Eleven Labs API
        generate_speech_elevenlabs(
            eleven_labs_api_key=eleven_labs_api_key,
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
    eleven_labs_api_key: str,
    text: str,
    voice_name: str,
    voice_id: str,
    output_dir: str,
    output_filename: str,
) -> None:
    """
    ElevenLabs API returns mp3 format data
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
        "xi-api-key": eleven_labs_api_key,
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
    generate_voice_baseline(
        args.eleven_labs_api_key, args.voice_name, args.voice_id, language=args.language
    )
