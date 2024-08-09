import argparse
import datetime
import glob
import os
import random
import subprocess
from dataclasses import dataclass
import csv
from functools import lru_cache
from typing import List, Optional, Any
import requests
import re
import torch
import torchaudio
from TTS.tts.configs.xtts_config import XttsConfig
from TTS.tts.models.xtts import Xtts


def parse_arguments():
    """
    Parse the command line arguments for the script. Use --help on the command line for more details.
    """
    parser = argparse.ArgumentParser(
        description="Automatically generate a custom voice pack for CrewChief using text-to-speech."
    )
    parser.add_argument(
        "--voice_name",
        # transform the value to strip out spaces
        type=lambda x: x.replace(" ", ""),
        required=True,
        help="Your custom name for this voice. Will be used as output directory name and appear in the CrewChief UI. Spaces will be removed, and probably avoid using UTF-8 or complex characters, but who knows?",
    )
    parser.add_argument(
        "--voice_name_tts",
        type=str,
        default=None,
        help="The name of the voice as it should be pronounced by the TTS engine. For example, you may have a voice_name of 'Luis' but a voice_name_tts of 'Luees'.  If not provided, the voice_name will be used. This may be used in the radio check messages.")
    parser.add_argument(
        "--your_name",
        type=str,
        default="",
        help="Your name, used by the Crew Chief to refer to you personally, baked into the generated audio. Defaults to empty text.",
    )
    parser.add_argument(
        "--variation_count",
        type=int,
        default=2,
        help="Number of additional variations to generate for each audio file. Set to 0 to disable variations.",
    )
    parser.add_argument(
        "--output_audio_dir",
        type=str,
        default="./output",
        help="Path to the directory where the generated audio files will be saved",
    )
    parser.add_argument(
        "--disable_audio_effects",
        action="store_true",
        help="Prevent applying audio effects to the generated audio files",
    )
    parser.add_argument(
        "--disable_text_replacements",
        action="store_true",
        help="Prevent applying text replacement rules to the generated audio files. Add or modify rules directly in generate_voice_pack.py.",
    )
    parser.add_argument(
        "--audio_inventory_file",
        type=str,
        default="./audio_file_inventory.csv",
        help="Path to the CSV file containing the audio inventory",
    )
    parser.add_argument(
        "--original_inventory_order",
        action="store_true",
        help="Do not randomize the order of the audio files in the inventory. Recommended to keep shuffling enabled when running multiple instances of the script in parallel.",
    )
    parser.add_argument(
        "--baseline_audio_dir",
        type=str,
        default="./output/baseline",
        help="Path to the directory containing the baseline audio recordings which will be used to clone that speaker's voice.",
    )
    parser.add_argument(
        "--skip_inventory",
        action="store_true",
        help="Skip generating audio files based on entries from the audio inventory file. Probably not what you want, but maybe useful during testing (for example, to skip directly to the radio check generation).",
    )
    parser.add_argument(
        "--skip_radio_check",
        action="store_true",
        help="Skip generating radio check audio clips.",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Overwrite existing audio files",
    )
    parser.add_argument(
        "--disable_deepspeed",
        action="store_true",
        help="Skip DeepSpeed during inference. Recommended to keep it enabled if possible as inference (TTS generation) is much faster, but it causes a longer startup time and noisy logs so may be helpful to disable during certain development steps.",
    )
    parser.add_argument(
        "--voicepack_version",
        type=str,
        default=datetime.datetime.now().strftime("%Y%m%d"),
        help="Version of the voice pack. This is used in the attribution file and elsewhere to identify newer or alternate versions. The default value is the current date.",
    )

    return parser.parse_args()


@dataclass
class CrewChiefAudioFile:
    def __init__(
        self,
        original_path: str,
        audio_filename: str,
        original_text: str,
        text_for_tts: str,
    ):
        self.original_path = original_path
        self.audio_filename = audio_filename
        self.original_text = original_text
        self.text_for_tts = text_for_tts


def parse_audio_inventory_file(inventory_file_path: str) -> List[CrewChiefAudioFile]:
    """
    Read the audio inventory file into a list of CrewChiefAudioFile objects.
    """
    entries: List[CrewChiefAudioFile] = []

    with open(inventory_file_path, newline="", encoding="utf-8") as csvfile:
        csvreader = csv.reader(csvfile)

        # skip header row
        next(csvreader)

        for row in csvreader:
            file_mapping, original_text, text_for_tts = row
            filepath, wav_filename = file_mapping.split(":")
            audio_filename = wav_filename.replace(".wav", "")
            filepath_fixed = filepath.replace("\\", "/")
            entries.append(
                CrewChiefAudioFile(
                    filepath_fixed, audio_filename, original_text, text_for_tts
                )
            )

    return entries


def apply_audio_effects(input_file: str, output_file: str) -> None:
    """
    Apply audio effects to the generated audio files:
    - slight gain reduction
    - equalizer adjustments to make it sound more like a motorsports radio call
    - slight overdrive
    - trim silence from both ends
    - normalize
    Note that noise is not added since the CrewChief overlays background noise separately.

    You are encouraged to modify these effects to suit your own preferences. It's unfortunately
    painful to find authoritative documentation for sox, but hopefully a Google search will help.
    """

    sox_command: List[str] = [
        "sox",
        "-V1",
        "-q",
        input_file,
        output_file,
        "pitch",
        "-90",
        "gain",
        "-3",
        "equalizer",
        "100",
        "0.5q",
        "-12",
        "equalizer",
        "200",
        "0.5q",
        "-6",
        "equalizer",
        "300",
        "0.5q",
        "-3",
        "equalizer",
        "3000",
        "0.5q",
        "6",
        "equalizer",
        "6000",
        "0.5q",
        "4",
        "equalizer",
        "10000",
        "0.5q",
        "3",
        "overdrive",
        "20",
        "30",
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
        "-1"
    ]

    try:
        subprocess.run(sox_command, check=True)
    except subprocess.CalledProcessError as e:
        print(f"An error occurred: {e}")


def is_invalid_wav_file(filename: str) -> bool:
    """
    TODO: implement this function, it should check if the file is a valid
    Acceptance criteria for a valid file:
    - no weird frequencies
    - not materially longer than other variants
    - not longer than expected based on the input text
    - file size is not over x MB
    - audio duration not over x seconds
    Return False if the caller should regenerate this file (ie, try again to make a clean file)
    """
    return True


@lru_cache(maxsize=None)
def init_xtts_model(use_deepspeed: bool = True) -> Any:
    """
    Initialize the Xtts model. This function is cached, so it will only run
    once, and the model will be reused for all subsequent calls.
    """
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
        use_deepspeed=use_deepspeed,
    )
    model.cuda()
    return model


@lru_cache(maxsize=None)
def init_xtts_latents(
    model: Any, reference_speaker_wav_paths: tuple
) -> tuple[Any, Any]:
    """
    Initialize the Xtts model and compute the speaker latents for the reference speaker.
    These embeddings are used to condition the generated speech to sound like the reference
    speaker, as represented in the "baseline" wav files for the voice you are cloning.

    Note that this function is cached, so it will only run once.
    """
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
    temperature: float = 0.3,
    speed: float = 1.4,
    overwrite: bool = False,
    use_deepspeed: bool = True,
    enable_audio_effects: bool = True,
) -> requests.Response:
    """
    Generate speech using the Coqui TTS framework and the multilingual xtts model.
    See README.md for more details on Coqui.
    """
    full_raw_filename = f"{output_path}/{output_filename}.raw.wav"
    full_output_filename = f"{output_path}/{output_filename}.wav"

    # immediately skip generating this file if it already exists (unless asked to overwrite)
    file_exists = os.path.isfile(full_output_filename) or os.path.isfile(
        full_raw_filename
    )
    if file_exists and not overwrite:
        print(f"File already exists, skipping: {full_output_filename}")
        return

    # ensure the output directory exists
    os.makedirs(output_path, exist_ok=True)

    # get a reference to the model and the speaker embeddings
    # these two calls are cached and only run the first time
    model = init_xtts_model(use_deepspeed=use_deepspeed)
    gpt_cond_latent, speaker_embedding = init_xtts_latents(
        model, tuple(reference_speaker_wav_paths)
    )

    # Temperature and speed are xtts model-specific parameters, and while you are encouraged
    # to experiment with these values, the values chosen below are known to work well for
    # many input voices -- and changing them much may greatly increase the chances of garbled
    # or corrupt output speech. Speed in particular is a tricky parameter to adjust.
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
    )

    # save the audio as 24KHz 32-bit PCM wav file named xxx.raw.wav
    torchaudio.save(full_raw_filename, torch.tensor(out["wav"]).unsqueeze(0), 24000)

    if enable_audio_effects:
        # apply audio effects to the generated audio file, creating a new file with
        # effects applied, enabling the deletion of the raw file
        apply_audio_effects(full_raw_filename, full_output_filename)
        os.remove(full_raw_filename)
    else:
        # just keep the raw file
        os.rename(full_raw_filename, full_output_filename)


    print(f"File created at: {full_output_filename}")


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


def generate_replacement_rules(your_name: str) -> List[ReplacementRule]:
    """
    Consider these ReplacementRules as very optional, you probably want to do most editing in the `audio_file_inventory.csv` file, since it's easier to simply edit the `text_for_tts` column to change the text that is used to generate the audio .wav file.
    """

    replacement_rules: List[ReplacementRule] = [
        # example: randomly replace most occurrences of `mate` with `bro`, `buddy`, `guy`, or `my man`
        ReplacementRule(
            category="improve_mate",
            regex=r"\bmate\b",
            replacement="bro",
            probability=0.2,
        ),
        ReplacementRule(
            category="improve_mate",
            regex=r"\bmate\b",
            replacement="buddy",
            probability=0.2,
        ),
        ReplacementRule(
            category="improve_mate",
            regex=r"\bmate\b",
            replacement="guy",
            probability=0.3,
        ),
        ReplacementRule(
            category="improve_mate",
            regex=r"\bmate\b",
            replacement="my man",
            probability=0.3,
        ),
        #
        # example: your name instead of `mate` (80% of the time, others stay `mate`)
        ReplacementRule(
            category="improve_mate",
            regex=r"\bmate\b",
            replacement=your_name,
            probability=0.8,
        ),
        #
        # example: replace all remaining occurrence of `mate` with nothing
        ReplacementRule(category="improve_mate", regex=r"\bmate\b", replacement=""),
        #
        # example: remove `mate` entirely. Use category name with apply_replacements() to toggle
        ReplacementRule(category="remove_mate", regex=r"\bmate\b", replacement=""),
        #
        # example: translate explicit words to suit regional preferences
        ReplacementRule(
            category="improve_bloody",
            regex=r"\bloody\b",
            replacement="damn",
            probability=1.0,
        ),
        # example: phonetically spelling out a hard-to-pronounce corner name.
        # alternately, consider editing the `text_for_tts` column in `audio_file_inventory.csv`
        ReplacementRule(category="fixes", regex=r"130R", replacement="one-thirty R"),
    ]
    return replacement_rules


def apply_replacements(
    text: str, rules: List[ReplacementRule], category: Optional[str] = None
) -> str:
    """
    Apply the replacement pattern specified by the list of ReplacementRule objects
    to the input text, producing modified output text. This is used for things like
    runtime replacement of one word with another without changing the audio
    inventory file.

    For example, if you want to replace all occurrences of "mate" with "buddy", it
    may be more convenient to do so with a ReplacementRule.
    """
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
    """
    ReplacementRules will default to disabled, this is a shortcut to turn on a certain
    category of changes or fixes while still maintaining a larger list of ReplacementRules
    some of which you want to keep disabled (ie, while experimenting).
    """
    for rule in rules:
        if rule.category == category:
            rule.active = activate


def main():
    """
    The main entry point for the script.
    """
    args = parse_arguments()

    output_file_prefix = f"{args.output_audio_dir}/{args.voice_name}"

    # setup some base parameters which can be reused across calls to the TTS generator
    coqui_tts_args = {
        "speed": 1.0,
        "temperature": random.uniform(0.2, 0.3),
        "reference_speaker_wav_paths": glob.glob(
            f"output/baseline/{args.voice_name}/*.wav"
        ),
        "overwrite": args.overwrite,
        "enable_audio_effects": not args.disable_audio_effects,
        "use_deepspeed": not args.disable_deepspeed,
    }

    if not args.skip_inventory:
        entries = parse_audio_inventory_file(args.audio_inventory_file)

        if len(entries) > 0:
            # create the output directory
            relative_output_dir = f"{args.output_audio_dir}/{args.voice_name}"
            full_output_dir = os.path.abspath(relative_output_dir)
            os.makedirs(full_output_dir, exist_ok=True)

            # TODO: write an attribution file which says something like
            # "Created for use with CrewChief (https://gitlab.com/mr_belowski/CrewChiefV4)
            # using crew-chief-autovoicepack: http://github.com/xxx"
            # and include it in the output directory
            attribution_filename = f"{relative_output_dir}/CREATED_BY.txt"
            with open(attribution_filename, "w") as f:
                f.write(
                    f"This voice pack was created using crew-chief-autovoicepack (https://github.com/cktlco/crew-chief-autovoicepack) for use with the venerable virtual race engineer application CrewChief (https://gitlab.com/mr_belowski/CrewChiefV4).\n\nVoice name: {args.voice_name}.\nVersion {args.voicepack_version}."
                )
                print(
                    f"Attribution file written to {attribution_filename} for voicepack '{args.voice_name}' version {args.voicepack_version}."
                )

        # Enable a quick way of globally replacing words in the original CrewChief text
        # before sending it to the text-to-speech step. This section just turns on the
        # rules you want to use. See the ReplacementRule examples for more details.
        replacement_rules = (
            []
            if args.disable_text_replacements
            else generate_replacement_rules(args.your_name)
        )

        # User adjustable! Feel free to enable or disable rules like these.
        activate_rules_by_category(replacement_rules, "remove_mate")
        activate_rules_by_category(replacement_rules, "improve_bloody")
        activate_rules_by_category(replacement_rules, "fixes")

        # Shuffle the entries so that the order of the audio file generation is randomized.
        # This helps multiple instances of the script to run in parallel without racing to
        # generate the same files
        if not args.original_inventory_order:
            random.shuffle(entries)

        # now for each entry in the audio inventory file, generate a speech .wav file
        for entry_idx, entry in enumerate(entries, 1):
            print(
                f"Generating audio for {entry_idx} - '{entry.original_text}' -> '{entry.text_for_tts}'"
            )

            # perform the actual text substitution based on the replacement rules enabled above
            filtered_text = (
                entry.text_for_tts
                if args.disable_text_replacements
                else apply_replacements(entry.text_for_tts, replacement_rules)
            )

            for variant_id in range(0, args.variation_count + 1):
                # "Variations" allow you to create additional audio files beyond those included
                # in the original CrewChief audio pack. This is intended to be useful primarily for
                # those phrases you hear very frequently (cut track warnings *achem*), and provides
                # another randomized call to the text-to-speech generator, so will provide slightly
                # different pronounciation/enunciation for each result, though the spoken text
                # will be identical. To add true textual variety, freely add additional rows to the
                # `audio_file_inventory.csv` file, copying from the original entries where you want
                # to add variety. See README for more details.
                #
                # Remember the entire storage required grows by this size, and the generated voices
                # here are already larger since they are saved as 32-bit 24KHz versus the original
                # 16-bit 22KHz CrewChief files, so a voice pack with 3 variants is ~2GB, while the
                # original CrewChief voice pack is ~0.5GB.

                if args.variation_count == 0:
                    # no changes, use the original filename
                    variant_filename = entry.audio_filename
                else:
                    # otherwise, adjust the filename so that it's unique
                    # CrewChief will happily read any filenames in the directory,
                    # though there are certain prefix/suffixes it uses to differentiate
                    # a subset of the generated files (for example, "rushed", "op_prefix", "sweary")
                    variant_tag = chr(variant_id + ord("a"))  # a-z
                    variant_filename = f"{entry.audio_filename}-{variant_tag}"

                # TODO: implement is_invalid_wav_file() and retry this up to x times, to
                #       automatically regenerate any malformed output files (too long, weird
                #       frequencies, etc)

                generate_speech_coqui_tts(
                    **coqui_tts_args,
                    text=filtered_text,
                    output_path=f"{output_file_prefix}{entry.original_path}",
                    output_filename=variant_filename,
                )

        print("All sounds from audio_file_inventory.csv have been generated.")

    # In addition to the normal audio files covered in the audio inventory file,
    # CrewChief also supports custom radio check messages aligned to the new
    # voice pack. This generates a few responses so that you don't have to hear
    # the same comment every time the app starts.
    if not args.skip_radio_check:
        print("Generating radio check audio clips...")
        voice_name_tts = args.voice_name_tts or args.voice_name
        # feel free to edit any or all of these to make your own custom phrases
        radio_check_phrases = [
            f"{voice_name_tts} here",
            "Radio's loud and clear",
            "Copy that, radio check",
            "Loud and clear",
            "Radio check",
            "You're coming in clear",
            f"{voice_name_tts} here, ready to help",
            f"{voice_name_tts} reading you, radio check",
            "Radio's good",
            "Clear signal, all good",
            "Check, check, radio's fine",
            "Radio's up, you're clear",
            "Loud and clear, over",
            "Radio check, all systems go",
            "You're clear on my end",
            "Radio's strong",
            "All good, radio's clear",
            "Copy, loud and clear",
            "Check",
            "Signal's clear, radio check",
            "You're loud and clear"
        ]
        for radio_check_idx, radio_check_phrase in enumerate(radio_check_phrases, 1):
            print(f"Generating radio check audio clip {radio_check_idx} - {radio_check_phrase}...")
            generate_speech_coqui_tts(
                **coqui_tts_args,
                text=radio_check_phrase,
                # the official requirement is to use this directory name per https://thecrewchief.org/showthread.php?825-Authoring-alternative-Crew-Chief-voice-packs
                # but since it's outside the voicepack root diretory the user will need to move it there manually
                output_path=f"{output_file_prefix}/radio_check_{args.voice_name}/test",
                output_filename=f"{radio_check_idx}",
            )
        print("All radio check audio clips have been generated.")

    print("All done.")


if __name__ == "__main__":
    print("Starting...")
    main()
