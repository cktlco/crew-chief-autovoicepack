import argparse
import datetime
import glob
import os
import random
import subprocess
from dataclasses import dataclass
import csv
from functools import lru_cache
from typing import List, Any
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
        help="Your custom name for this voice. Will be used as output directory name and appear in the CrewChief UI. Spaces will be removed, and probably avoid using UTF-8 and other characters.",
    )
    parser.add_argument(
        "--voice_name_tts",
        type=str,
        default=None,
        help="The name of the voice as it should be pronounced by the TTS engine. For example, you may have a voice_name of 'Luis' but a voice_name_tts of 'Luees'.  If not provided, the voice_name will be used. This may be used in the radio check messages.",
    )
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
        "--phrase_inventory",
        type=str,
        default="./phrase_inventory.csv",
        help="Path to the CSV file containing a list of all the audio files to create alongside the text to be used to generate them. The documentation refers to this as the 'phrase inventory', and populated with all the 'Jim' voicepack phrases from CrewChiefV4.",
    )
    parser.add_argument(
        "--original_inventory_order",
        action="store_true",
        help="Do not randomize the order of the audio files in the inventory. It's recommended to keep shuffling enabled (omit this option) when running multiple instances of the script in parallel.",
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
        help="Skip generating audio files based on entries from the audio file inventory. Probably not what you want, but maybe useful during testing (for example, to skip directly to the radio check generation).",
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
    parser.add_argument(
        "--cpu_only",
        action="store_true",
        help="Run the process on the CPU instead of the GPU. This is much slower but is necessary if your PC does not have an CUDA-capable NVIDIA GPU. Implies --disable_deepspeed.",
    )
    parser.add_argument(
        "--keep_invalid_files",
        action="store_true",
        help="Keep invalid .wav files around with a modified name instead of deleting them. This is useful for debugging and understanding why a file was considered invalid, but you'd want to remove these from a final shareable voice pack.",
    )

    return parser.parse_args()


@dataclass
class CrewChiefAudioFile:
    """
    A simple data structure aligned to the contents of the audio file inventory.
    """

    def __init__(
        self,
        audio_path: str,
        audio_filename: str,
        subtitle: str,
        text_for_tts: str,
    ):
        self.audio_path = audio_path
        self.audio_filename = audio_filename
        self.subtitle = subtitle
        self.text_for_tts = text_for_tts
        self.audio_path_filtered = ""
        self.subtitle_filtered = ""
        self.text_for_tts_filtered = ""


def parse_phrase_inventory(inventory_file_path: str) -> List[CrewChiefAudioFile]:
    """
    Read the audio file inventory into a list of CrewChiefAudioFile objects.
    """
    entries: List[CrewChiefAudioFile] = []

    with open(inventory_file_path, newline="", encoding="utf-8") as csvfile:
        csvreader = csv.reader(csvfile)

        # skip header row
        next(csvreader)

        # read each row of the csv file in one at a time
        for row in csvreader:
            audio_path_windows, audio_filename_with_ext, subtitle, text_for_tts = row

            audio_filename = audio_filename_with_ext.replace(".wav", "")
            # swap from backslashes (Windows) to forward slashes (Linux)
            audio_path = audio_path_windows.replace("\\", "/")

            # put the csv file data into a more friendly data structure
            entries.append(
                CrewChiefAudioFile(
                    audio_path, audio_filename, subtitle, text_for_tts
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
    painful to find authoritative documentation for sox.
    """

    sox_command: List[str] = [
        "sox",
        "-V1",
        "-q",
        input_file,
        output_file,
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
        "7",
        "12",
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
        "-1",
    ]

    try:
        subprocess.run(sox_command, check=True)
    except subprocess.CalledProcessError as e:
        print(f"An error occurred: {e}")
        # TODO: raise the error for the caller


def is_invalid_wav_file(file_path: str, tts_text: str) -> bool:
    """
    # TODO: keep adding to these checks
    Acceptance criteria for a valid file:
    - no periods of silence longer than x seconds
    - not longer than expected based on the input text
    - file size is not over x MB
    - audio duration not over x seconds
    - not materially longer than its other variants
    - no weird frequencies (?)

    Return False if the caller should regenerate this file (ie, try again to make a clean file)
    """
    is_invalid = (
        detect_excess_silence(
            file_path=file_path, silence_threshold=0.36 if len(tts_text) < 30 else 0.6
        )
        or detect_invalid_filesize(file_path)
        or detect_invalid_audio_duration(file_path=file_path, tts_text=tts_text)
    )

    if is_invalid:
        print(f"Invalid .wav file detected: {file_path}")

    return is_invalid


def detect_invalid_audio_duration(file_path: str, tts_text: str) -> bool:
    """
    Returns true if the audio duration is too long for the given text, based on
    the number of characters in the text and a rough estimate of speaking rate.
    """

    # generous estimate of speaking rate in characters per second
    speaking_rate = 3
    minimum_expected_duration = 1.5

    # calculate the expected duration based on the text
    expected_duration = len(tts_text) / speaking_rate + minimum_expected_duration

    # get the actual duration of the audio file
    audio_info = torchaudio.info(file_path)
    actual_duration = audio_info.num_frames / audio_info.sample_rate

    if actual_duration > expected_duration:
        print(
            f"Invalid audio duration detected for text '{tts_text}'. Expected: {expected_duration:.2f}s, Actual: {actual_duration:.2f}s"
        )
        return True

    return False


def detect_invalid_filesize(file_path: str, max_valid_size: int = 1000000) -> bool:
    """
    Returns True if the input audio file is (arbitrarily) too large.
    Used as a crude filter for "bad" results from the TTS engine.
    Default is 1MB (1000000 bytes).
    """
    if os.path.getsize(file_path) > max_valid_size:
        print(f"Invalid file size detected. File too large: {file_path}")
        return True
    return False


def detect_excess_silence(file_path: str, silence_threshold: float) -> bool:
    """
    Returns True if the input audio file has any silence longer than the given threshold.
    """
    try:
        result = subprocess.run(
            [
                "ffmpeg",
                "-i",
                file_path,
                "-af",
                f"silencedetect=n=-50dB:d={silence_threshold}",
                "-f",
                "null",
                "-",
            ],
            stderr=subprocess.PIPE,
            text=True,
            check=True,
        )

        # Search for silence_duration in the output
        for line in result.stderr.splitlines():
            if "silence_duration" in line:
                duration_str = line.split("silence_duration: ")[-1].split(" ")[0]
                silence_duration = float(duration_str)
                if silence_duration > silence_threshold:
                    print(
                        f"Excess silence detected in file {file_path}: {silence_duration:.2f} seconds"
                    )
                    return True

    except subprocess.CalledProcessError as e:
        print(f"Error processing file {file_path}: {e}")
        return False

    return False


@lru_cache(maxsize=None)
def init_xtts_model(cpu_only: bool = False, use_deepspeed: bool = True) -> Any:
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
    if not cpu_only:
        model.cuda()
    else:
        model.cpu()

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


def generate_speech(
    text: str,
    output_path: str,
    output_filename: str,
    reference_speaker_wav_paths: List[str],
    temperature: float = 0.3,
    speed: float = 1.2,
    overwrite: bool = False,
    cpu_only: bool = False,
    use_deepspeed: bool = True,
    enable_audio_effects: bool = True,
    keep_invalid_files: bool = True,
):
    """
    Create a .wav file based on the input text and the reference speaker's voice.
    """

    # until the output passes the is_invalid_wav_file check, keep trying up to this many times
    max_attempts = 30

    for attempt_idx in range(max_attempts):
        # current implementation: coqui_tts
        generate_speech_coqui_tts(
            text=text,
            output_path=output_path,
            output_filename=output_filename,
            reference_speaker_wav_paths=reference_speaker_wav_paths,
            temperature=temperature,
            speed=speed,
            overwrite=overwrite,
            cpu_only=cpu_only,
            use_deepspeed=use_deepspeed,
            enable_audio_effects=enable_audio_effects,
        )

        file_path = f"{output_path}/{output_filename}.wav"

        if is_invalid_wav_file(file_path=file_path, tts_text=text):
            print(f"Regenerating invalid .wav file: {output_filename}")

            if keep_invalid_files:
                # keep it around with a modified name
                os.rename(
                    file_path,
                    f"{output_path}/{output_filename}.invalid-{attempt_idx}.wav",
                )
            else:
                os.remove(f"{output_path}/{output_filename}.wav")

            overwrite = True

        else:
            break

    else:
        print(
            f"Failed to generate a clean .wav file after {max_attempts} attempts: {output_filename}"
        )


def generate_speech_coqui_tts(
    text: str,
    output_path: str,
    output_filename: str,
    reference_speaker_wav_paths: List[str],
    temperature: float = 0.3,
    speed: float = 1.2,
    overwrite: bool = False,
    cpu_only: bool = False,
    use_deepspeed: bool = True,
    enable_audio_effects: bool = True,
) -> None:
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
        print(f"File exists, skipping: {full_output_filename}")
        return

    # ensure the output directory exists
    os.makedirs(output_path, exist_ok=True)

    # get a reference to the model and the speaker embeddings
    # these two calls are cached and only run the first time
    model = init_xtts_model(cpu_only=cpu_only, use_deepspeed=use_deepspeed)
    gpt_cond_latent, speaker_embedding = init_xtts_latents(
        model, tuple(reference_speaker_wav_paths)
    )

    # Most of these are xtts model-specific parameters, and while you are encouraged
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

    print(f"Audio file created: {full_output_filename}")


@dataclass
class ReplacementRule:
    regex: str
    replacement: str
    probability: float = (
        1.0  # Probability to apply the replacement, 1.0 means always apply
    )


def generate_replacement_rules(your_name: str) -> List[ReplacementRule]:
    """
    Consider these ReplacementRules as very optional, you probably want to do most editing in the `phrase_inventory.csv` file, since it's easier to simply edit the `text_for_tts` column to change the text that is used to generate the audio .wav file.
    """

    replacement_rules: List[ReplacementRule] = [
        # example: your name instead of `mate` (80% of the time, others stay `mate`)
        ReplacementRule(
            regex=r"\bmate\b",
            replacement=your_name,
            probability=0.8,
        ),
        # example: randomly replace some remaining `mate` with `buddy`
        ReplacementRule(
            regex=r"\bmate\b",
            replacement="buddy",
            probability=0.2,
        ),
        #
        # example: replace all remaining occurrence of `mate` with nothing
        ReplacementRule(regex=r"\bmate\b", replacement=""),
        #
        # example: translate explicit words to suit regional preferences
        ReplacementRule(
            regex=r"\bloody\b",
            replacement="damn",
            probability=1.0,
        ),
        # example: phonetically spelling out a hard-to-pronounce corner name.
        # alternately, consider editing the `text_for_tts` column in `phrase_inventory.csv`
        ReplacementRule(regex=r"130R", replacement="one-thirty R"),
    ]
    return replacement_rules


def apply_replacements(text: str, rules: List[ReplacementRule]) -> str:
    """
    Apply the replacement pattern specified by the list of ReplacementRule objects
    to the input text, producing modified output text. This is used for things like
    runtime replacement of one word with another without changing the audio
    inventory file.

    For example, if you want to replace all occurrences of "mate" with "buddy", it
    may be more convenient to do so with a ReplacementRule rather than search/replace
    directly in the audio file inventory.
    """
    for rule in rules:
        if re.search(rule.regex, text) and random.random() <= rule.probability:
            print(f"Replacing '{rule.regex}' with '{rule.replacement}' in '{text}'")
            text = re.sub(rule.regex, rule.replacement, text)
            print(f"New value is: {text}")
    return text


def main():
    """
    The main entry point for the script
    """
    args = parse_arguments()

    voicepack_base_dir = f"{args.output_audio_dir}/{args.voice_name}"

    # setup some base parameters which can be reused across calls to the TTS generator
    tts_args = {
        "speed": 1.2,
        "temperature": random.uniform(0.2, 0.3),
        "reference_speaker_wav_paths": glob.glob(
            f"output/baseline/{args.voice_name}/*.wav"
        ),
        "overwrite": args.overwrite,
        "enable_audio_effects": not args.disable_audio_effects,
        "cpu_only": args.cpu_only,
        "use_deepspeed": (not args.disable_deepspeed) and (not args.cpu_only),
        "keep_invalid_files": args.keep_invalid_files,
    }

    if not args.skip_inventory:
        entries = parse_phrase_inventory(args.phrase_inventory)

        if len(entries) > 0:
            # create the output directory
            relative_output_dir = f"{args.output_audio_dir}/{args.voice_name}"
            full_output_dir = os.path.abspath(relative_output_dir)
            os.makedirs(full_output_dir, exist_ok=True)

            # create an attribution text file with some basic provenance, include in the output directory
            attribution_filename = f"{relative_output_dir}/CREATED_BY.txt"
            with open(attribution_filename, "w") as f:
                f.write(
                    f"""This voice pack was created using crew-chief-autovoicepack
(https://github.com/cktlco/crew-chief-autovoicepack)

...for use with the venerable virtual race engineer application CrewChief
(https://thecrewchief.org/)
(https://gitlab.com/mr_belowski/CrewChiefV4)

Voice name: {args.voice_name}
Version {args.voicepack_version}
"""
                )
                print(
                    f"Attribution file written to {attribution_filename} for voicepack '{args.voice_name}' version {args.voicepack_version}."
                )

        # Enable a quick way of globally replacing words in the original CrewChief text
        # before sending it to the text-to-speech step. This section establishes the potential
        # replacements. See the ReplacementRule examples for more details.
        replacement_rules = (
            []
            if args.disable_text_replacements
            else generate_replacement_rules(args.your_name)
        )

        # Shuffle the CrewChief phrases so that the order of the audio file generation is randomized.
        # This helps multiple instances of the script run in parallel without racing to
        # generate the same files
        if not args.original_inventory_order:
            random.shuffle(entries)

        # for each entry in the audio file inventory, generate a speech .wav file
        for entry_idx, entry in enumerate(entries, 1):
            print(
                f"Considering phrase {entry_idx} - '{entry.subtitle}' -> '{entry.text_for_tts}'"
            )

            # perform the actual text substitution based on the replacement rules enabled above
            # also replace any instances of `YOUR_NAME` with user's name (or blank if not provided)
            entry.text_for_tts_filtered = (
                entry.text_for_tts
                if args.disable_text_replacements
                else apply_replacements(entry.text_for_tts, replacement_rules)
            ).replace("YOUR_NAME", args.your_name)

            entry.audio_path_filtered = entry.audio_path.replace("YOUR_NAME", args.your_name)
            entry.subtitle_filtered = entry.subtitle.replace("YOUR_NAME", args.your_name)

            for variant_id in range(0, args.variation_count + 1):
                # "Variations" here means creating 1 or more additional audio files
                # based on the same text. The original CrewChief voice pack has only
                # one audio file per phrase, but the `variation_count` parameter here
                # can be set to 1 or more to create additional files with slightly
                # different pronounciation/enunciation and to give variety. It helps
                # by giving CrewChief more options to choose from when playing any
                # particular phrase, which can help reduce the feeling of repetition.
                #
                # To add true textual variety, freely add additional rows to the
                # `phrase_inventory.csv` file, copying from the original entries where you want
                # to add variety. See README for more details.
                #
                # Remember the entire storage required grows by the variant count, and the generated
                # voices here are already larger since they are saved as 32-bit 24KHz versus the
                # original 16-bit 22KHz CrewChief files, so a voice pack with 3 variants is ~2GB,
                # while the original CrewChief voice pack is ~0.5GB.

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

                # finally, generate and save a .wav file based on the phrase's text
                generate_speech(
                    **tts_args,
                    text=entry.text_for_tts_filtered,
                    output_path=f"{voicepack_base_dir}{entry.audio_path_filtered}",
                    output_filename=variant_filename,
                )

        print(f"All entries in {args.phrase_inventory} have been generated.")


        # write subtitles.csv files for each subfolder, following the convention of CrewChiefV4
        subtitle_entries = {}
        for entry in entries:
            if entry.audio_path_filtered not in subtitle_entries:
                subtitle_entries[entry.audio_path_filtered] = []
            subtitle_entries[entry.audio_path_filtered].append((entry.audio_filename, entry.subtitle))

        for subtitle_path, entry_details in subtitle_entries.items():
            subtitle_filename = f"{voicepack_base_dir}{subtitle_path}/subtitles.csv"
            if os.path.isfile(subtitle_filename):
                print(f"Skipping subtitles.csv since it exists at {subtitle_path}")
            else:
                print(f"Creating subtitles.csv for {subtitle_path}")
                with open(subtitle_filename, "w") as f:
                    for audio_filename, subtitle in entry_details:
                        for variant_id in range(0, args.variation_count + 1):
                            variant_tag = chr(variant_id + ord("a"))
                            f.write(f"{variant_tag}.wav,\"{subtitle}\"\n")

        print("All subtitles.csv files have been created.")

    # In addition to the normal audio files covered in the audio file inventory,
    # CrewChief also supports custom radio check messages aligned to the new
    # voice pack. This generates a few responses so that you don't have to hear
    # the same comment every time the app starts. Feel free to prune or supplement.
    if not args.skip_radio_check:
        print("Generating radio check audio clips...")
        voice_name_tts = args.voice_name_tts or args.voice_name
        # feel free to edit any or all of these to make your own custom phrases
        radio_check_phrases = [
            f"Engineer {voice_name_tts} confirming radio",
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
            "You're loud and clear",
        ]
        for radio_check_idx, radio_check_phrase in enumerate(radio_check_phrases, 1):
            print(
                f"Generating radio check audio clip {radio_check_idx} - {radio_check_phrase}..."
            )
            generate_speech(
                **tts_args,
                text=radio_check_phrase,
                # since the CrewChief-required location for radio_check messages is outside the voicepack
                # root directory, the user will need to move it there manually
                # "test" is the official CrewChief folder name for radio check messages
                output_path=f"{voicepack_base_dir}/radio_check_{args.voice_name}/test",
                output_filename=f"{radio_check_idx}",
            )
        print("All radio check audio clips have been generated.")


    # TODO: generate audio for the driver_names folder, optionally either including all the CrewChief names
    #       (from a static JSON file in this repo) or just a single name based on args.your_name with a dozen variants

    # TODO: generate optional spotter audio pack

    print("All done.")


if __name__ == "__main__":
    print("Starting...")
    main()
