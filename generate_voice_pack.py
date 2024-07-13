import os
import random
import shutil
import subprocess
from dataclasses import dataclass
import csv
import time
from functools import lru_cache
from typing import List, Optional, Dict, Any
import requests
import re
import torch
import torchaudio

from TTS.tts.configs.xtts_config import XttsConfig
from TTS.tts.models.xtts import Xtts

# ELEVEN_LABS_API_KEY = "fd1ff82b4244acc631d2257d24ef6a4c"
ELEVEN_LABS_API_KEY = "sk_f8af6014f4721cf708d801da3c16e05000e90e938e37c898"
COST_PER_CHAR = 0.00011


@dataclass
class VoiceEntry:
    filepath: str
    audio_filename: str
    text: str


def parse_csv(file_path: str) -> List[VoiceEntry]:
    entries: List[VoiceEntry] = []

    with open(file_path, newline="", encoding="utf-8") as csvfile:
        csvreader = csv.reader(csvfile)
        for row in csvreader:
            file_mapping, text = row
            subtitle_filepath, wav_filename = file_mapping.split(":")
            audio_filename = wav_filename.replace(".wav", "")
            subtitle_filepath_fixed = subtitle_filepath.replace("\\", "/")
            entries.append(VoiceEntry(subtitle_filepath_fixed, audio_filename, text))

    return entries


def make_louder_voicepack():
    """
    find mercury -type f -name "*.wav" -exec sh -c '
      output_dir="mercury-loud$(dirname "$1" | sed "s|^mercury||")"
      mkdir -p "$output_dir"
      output_file="$output_dir/$(basename "$1")"
      ffmpeg -i "$1" -af "dynaudnorm=f=150:g=15,volume=9dB" "$output_file"
    ' _ {} \;
    """
    pass


@lru_cache(maxsize=None)
def init_xtts_model() -> Any:
    print("xtts - Loading model...")
    model_path = (
        "/root/.local/share/tts/tts_models--multilingual--multi-dataset--xtts_v2"
    )
    config = XttsConfig()
    config.load_json(f"{model_path}/config.json")
    model = Xtts.init_from_config(config)
    model.load_checkpoint(
        config,
        checkpoint_dir=model_path,
        use_deepspeed=False,
    )
    model.cuda()
    return model


@lru_cache(maxsize=None)
def init_xtts_latents(reference_speaker_wav_paths: tuple) -> tuple[Any, Any]:
    model = init_xtts_model()

    print("xtts - Computing speaker latents...")
    gpt_cond_latent, speaker_embedding = model.get_conditioning_latents(
        audio_path=list(reference_speaker_wav_paths)
    )
    return gpt_cond_latent, speaker_embedding


def generate_speech_coqui_tts(
    text: str,
    output_path: str,
    output_filename: str,
    reference_speaker_wav_paths: List[str],
    voice_name: str,
    temperature: float = 0.3,
    speed: float = 1.0,
) -> requests.Response:
    full_output_path = f"output/{voice_name}{output_path}"
    full_output_filename = f"{full_output_path}/{output_filename}.wav"

    os.makedirs(full_output_path, exist_ok=True)

    if os.path.isfile(full_output_filename):
        print(f"File already exists: {full_output_filename}")
    else:
        # these two calls are cached and only run the first time
        model = init_xtts_model()
        gpt_cond_latent, speaker_embedding = init_xtts_latents(
            tuple(reference_speaker_wav_paths)
        )

        out = model.inference(
            text,
            "en",
            gpt_cond_latent,
            speaker_embedding,
            temperature=temperature,
            top_k=50,
            top_p=0.8,
            speed=speed,
            length_penalty=1.0,
            repetition_penalty=4.0,
            enable_text_splitting=False,
            # num_gpt_outputs=16,
            # gpt_cond_len=90,
            # gpt_cond_chunk_len=4,
            # max_ref_len=30,
            # sound_norm_refs=False
        )

        torchaudio.save(
            full_output_filename, torch.tensor(out["wav"]).unsqueeze(0), 24000
        )

        print(f"File created at: {full_output_filename}")


def generate_speech_alltalk(
    text: str,
    output_path: str,
    output_filename: str,
    text_filtering: str = "none",
    text_not_inside: str = "character",
    language: str = "en",
    voice_name: str = "mercury",
    internal_output_filename: str = "test2",
    internal_output_usetimestamp: bool = True,
    decibels_volume_increase: float = 0.0,
    autoplay: bool = False,
    autoplay_volume: float = 1.0,
    speed: float = 1.25,
) -> requests.Response:
    url = "http://127.0.0.1:7851/api/tts-generate"
    voice_map: Dict[str, str] = {
        "mercury": "female_06.wav",
        "elm": "David_Attenborough CC3.wav",
    }
    alltalk_voice_name: str = voice_map[voice_name]

    data = {
        "text_input": text,
        "text_filtering": text_filtering,
        "character_voice_gen": alltalk_voice_name,
        "narrator_enabled": "silent",
        "narrator_voice_gen": alltalk_voice_name,
        "text_not_inside": text_not_inside,
        "language": language,
        "output_file_name": internal_output_filename,
        "output_file_timestamp": str(internal_output_usetimestamp).lower(),
        "autoplay": str(autoplay).lower(),
        "autoplay_volume": autoplay_volume,
        "speed": speed,
    }

    full_output_path = f"output/{voice_name}{output_path}"
    full_output_filename = f"{full_output_path}/{output_filename}.wav"

    if os.path.isfile(full_output_filename):
        print(f"File already exists: {full_output_filename}")
    else:
        response = requests.post(url, data=data)
        result = response.json()

        if response.status_code == 200:
            if result["status"] == "generate-success":
                original_path = result["output_file_path"]
                os.makedirs(os.path.dirname(full_output_filename), exist_ok=True)

                if decibels_volume_increase == 0.0:
                    try:
                        shutil.move(original_path, full_output_filename)
                    except FileNotFoundError:
                        print(
                            "File not found when trying to move. Pausing for 3 seconds, then retrying..."
                        )
                        time.sleep(3)
                        shutil.move(original_path, full_output_filename)
                else:
                    temp_output_filename = full_output_filename + "-temp.wav"
                    try:
                        subprocess.run(
                            [
                                "ffmpeg",
                                "-i",
                                original_path,
                                "-af",
                                f"dynaudnorm=f=150:g=15,volume={decibels_volume_increase}dB",
                                temp_output_filename,
                            ],
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE,
                        )
                        shutil.move(temp_output_filename, full_output_filename)
                    except FileNotFoundError:
                        print(
                            "File not found when trying to process with ffmpeg. Pausing for 3 seconds, then retrying..."
                        )
                        time.sleep(3)
                        subprocess.run(
                            [
                                "ffmpeg",
                                "-i",
                                original_path,
                                "-af",
                                f"dynaudnorm=f=150:g=15,volume={decibels_volume_increase}dB",
                                temp_output_filename,
                            ],
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE,
                        )
                        shutil.move(temp_output_filename, full_output_filename)

                print(f"File moved to: {full_output_filename}")
        else:
            print(f"Error: {response.status_code}, {response.text}")


def generate_speech_elevenlabs(
    text: str, output_path: str, output_filename: str
) -> None:
    # eleven labs API only returns mp3 format, so convert using `ffmpeg -i x.mp3 x.wav` offline

    voice = "ella"
    voices = {"neil": "vaxRW1dvOXCtu5h8p6Bl", "ella": "n6jOstWat2qlAEHuBjId"}
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voices[voice]}"

    full_output_path = f"output/{voice}{output_path}"
    full_output_filename = f"{full_output_path}/{output_filename}.mp3"
    if os.path.isfile(full_output_filename):
        # already exists, so don't make the API call
        print(f"File already exists: {full_output_filename}")
    else:
        os.makedirs(full_output_path, exist_ok=True)

        payload = {
            "text": text,
            "voice_settings": {
                "stability": 0.5,
                "similarity_boost": 0.75,
                "style": 0.0,
                "use_speaker_boost": True,
            },
            # "pronunciation_dictionary_locators": [
            #     {
            #         "pronunciation_dictionary_id": "<string>",
            #         "version_id": "<string>"
            #     }
            # ],
            "seed": random.randrange(1, 9999999),
            # "previous_text": "<string>",
            # "next_text": "<string>",
            # "previous_request_ids": ["<string>"],
            # "next_request_ids": ["<string>"]
        }
        headers = {
            "Content-Type": "application/json",
            "xi-api-key": ELEVEN_LABS_API_KEY,
        }

        response = requests.request("POST", url, json=payload, headers=headers)

        if response.status_code == 200:
            with open(full_output_filename, "wb") as f:
                for chunk in response.iter_content(chunk_size=1024):
                    if chunk:
                        f.write(chunk)
        else:
            print(
                f"Error from Eleven Labs API: {response.status_code} - {response.text}"
            )


@dataclass
class ReplacementRule:
    category: str
    regex: str
    replacement: str
    description: str = ""
    active: bool = False
    probability: float = (
        1.0  # Probability to apply the replacement, 1.0 means always apply
    )


replacement_rules: List[ReplacementRule] = [
    ReplacementRule(
        category="improve_mate", regex=r"\bmate\b", replacement="bro", probability=0.2
    ),
    ReplacementRule(
        category="improve_mate", regex=r"\bmate\b", replacement="buddy", probability=0.2
    ),
    ReplacementRule(
        category="improve_mate", regex=r"\bmate\b", replacement="guy", probability=0.3
    ),
    ReplacementRule(
        category="improve_mate",
        regex=r"\bmate\b",
        replacement="my man",
        probability=0.3,
    ),
    ReplacementRule(
        category="improve_mate", regex=r"\bmate\b", replacement="Blake", probability=0.8
    ),
    ReplacementRule(category="improve_mate", regex=r"\bmate\b", replacement=""),
    ReplacementRule(category="remove_mate", regex=r"\bmate\b", replacement=""),
    ReplacementRule(
        category="improve_bloody",
        regex=r"\bloody\b",
        replacement="damn",
        probability=1.0,
    ),
    ReplacementRule(category="fixes", regex=r"130R", replacement="one-thirty R", active=True),
]


def apply_replacements(
    text: str, rules: List[ReplacementRule], category: Optional[str] = None
) -> str:
    for rule in rules:
        if rule.active and (category is None or rule.category == category):
            if re.search(rule.regex, text) and random.random() <= rule.probability:
                print(f"Replacing '{rule.regex}' with '{rule.replacement}' in '{text}'")
                text = re.sub(rule.regex, rule.replacement, text)
                print(f"New value is: {text}")
    return text


def activate_rules_by_category(
    rules: List[ReplacementRule], category: str, activate: bool = True
) -> None:
    for rule in rules:
        if rule.category == category:
            rule.active = activate


def main():
    file_path = "./transcript.csv"

    entries = parse_csv(file_path)
    total_count = 0
    total_chars = 0
    total_cost = 0

    variations = 5  # keep it less than 25

    activate_rules_by_category(replacement_rules, "remove_mate")
    activate_rules_by_category(replacement_rules, "improve_bloody")

    random.shuffle(entries)
    for entry_idx, entry in enumerate(entries, 1):
        print(f"Generating audio for {entry_idx} - '{entry.text}'")
        print(entry)

        output_path = f"{entry.filepath}"
        total_count += 1
        total_chars += len(entry.text)
        total_cost += COST_PER_CHAR * len(entry.text)

        filtered_text = apply_replacements(entry.text, replacement_rules)

        for variant_id in range(1, variations):
            variant_suffix = chr(variant_id + ord('a'))
            variant_filename = f"{entry.audio_filename}-{variant_suffix}"

            # generate_speech_elevenlabs(text=filtered_text, output_path=output_path, output_filename=entry.audio_filename)
            # generate_speech_alltalk(voice_name="mercury", text=filtered_text, output_path=output_path, output_filename=entry.audio_filename,
            #                        decibels_volume_increase=6.0, speed=1.25)
            # generate_speech_alltalk(voice_name="elm", text=filtered_text, output_path=output_path, output_filename=entry.audio_filename,
            #                        decibels_volume_increase=6.0, speed=1.50)
            # generate_speech_coqui_tts(
            #     voice_name="blake",
            #     text=filtered_text,
            #     speed=random.uniform(1.49, 1.51),
            #     temperature=random.uniform(0.01, 0.1),
            #     output_path=output_path,
            #     output_filename=variant_filename,
            #     reference_speaker_wav_paths=[
            #         "blake-1.wav",
            #         "blake-2.wav",
            #         "blake-3.wav",
            #     ],
            # )
            generate_speech_coqui_tts(
                voice_name="belinda",
                text=filtered_text,
                speed=random.uniform(1.40, 1.51),
                temperature=random.uniform(0.1, 0.3),
                output_path=output_path,
                output_filename=variant_filename,
                reference_speaker_wav_paths=[
                    "belinda.wav"
                ],
            )
        print("")
        print("")

    print("All done.")
    # print(f"Total Cost: ${round(total_cost,2)} for {total_count} phrases and {total_chars} characters")


if __name__ == "__main__":
    print("Starting...")
    main()
