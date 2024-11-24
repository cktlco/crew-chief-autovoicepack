import logging
import argparse
import datetime
import glob
import os
import random
import subprocess
import time
from dataclasses import dataclass
from functools import lru_cache
from typing import List, Any, Optional
import re
import torch
import torchaudio
from torch.utils.data import DataLoader
from TTS.tts.configs.xtts_config import XttsConfig
from TTS.tts.models.xtts import Xtts
from xtts_integrity.transform import InferenceAudioTransform
from xtts_integrity.infer import AudioInferenceDataset, load_model, run_inference

from utils import CrewChiefAudioFile, parse_phrase_inventory

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()],
)


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
        default="Champ",
        help="Your name, used by the Crew Chief to refer to you personally, baked into the generated audio. Defaults to 'Champ', probably ok to be empty text also.",
    )
    parser.add_argument(
        "--variation_count",
        type=int,
        default=2,
        help="Number of additional variations to generate for each audio file. Default is 2. Set to 0 to disable variations.",
    )
    parser.add_argument(
        "--cpu_only",
        action="store_true",
        help="Run the process using the computer's Central Processing Unit (CPU) only, ignoring any available Graphics Processing Units (GPU). This is much slower but is necessary if your PC does not have an CUDA-capable NVIDIA GPU. Implies --disable_deepspeed.",
    )
    parser.add_argument(
        "--output_audio_dir",
        type=str,
        default="./output",
        help="Path to the directory where the generated audio files will be saved",
    )
    parser.add_argument(
        "--original_inventory_order",
        action="store_true",
        help="Do not randomize the order of the audio files in the inventory. It's recommended to keep shuffling enabled (omit this option) when running multiple instances of the script in parallel.",
    )
    parser.add_argument(
        "--phrase_inventory",
        type=str,
        default="./phrase_inventory.csv",
        help="Path to the CSV file containing a list of all the audio files to create alongside the text to be used to generate them. The documentation refers to this as the 'phrase inventory', and populated with all the 'Jim' voicepack phrases from CrewChiefV4.",
    )
    parser.add_argument(
        "--baseline_audio_dir",
        type=str,
        default="./baseline",
        help="Path to the directory containing the **baseline audio recordings** used to initialize the TTS model.",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Overwrite existing audio files. Note that if running multiple instances of the script in parallel, this means all replicas will perform all the work each (not what you want).",
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
        "--keep_invalid_files",
        action="store_true",
        help="Keep invalid .wav files around with a modified name instead of deleting them. This is useful for debugging and understanding why a file was considered invalid, but you'd want to remove these from a final shareable voice pack.",
    )
    parser.add_argument(
        "--max_invalid_attempts",
        type=int,
        default=30,
        help="Maximum number of attempts to generate a valid .wav file before giving up. This is used to prevent the script from getting stuck on a single problematic phrase, but keeping it high naturally encourages higher-quality audio output.",
    )
    parser.add_argument(
        "--radio_check_tts_text",
        type=str,
        default=None,
        help="Custom text to use for the radio check audio clips. If not provided, a default set of radio check phrases will be used. This is mainly useful for voicepack languages other than English.",
    )
    parser.add_argument(
        "--simple_validity_check",
        action="store_true",
        help="Use the legacy validity check for .wav files. This will bypass the xtts-integrity model validation output and use a simple check for silence and file size",
    )
    parser.add_argument(
        "--xtts_speed",
        type=float,
        default=1.6,
        help="Speed factor for the TTS engine. Somewhat arbitrary, but a value of 1.2-1.7 is recommended.",
    )
    parser.add_argument(
        "--xtts_integrity_threshold",
        type=float,
        default=0.9,
        help="Threshold for the xtts-integrity model to consider a .wav file valid. This is a value between 0 and 1, where a higher value means the model will be more strict in what it considers valid. Lowering this value will allow more files to pass the validity check, but may also allow more audio artifacts to slip through.",
    )
    parser.add_argument(
        "--progress_check_interval",
        type=float,
        default=30.0,
        help="Interval in seconds between progress updates (which may be expensive/slow to calculate since it scans the entire output directory).",
    )
    return parser.parse_args()


def apply_audio_effects(input_file: str, output_file: str) -> None:
    """
    Apply audio effects to the generated audio files:
    - equalizer adjustments to make it sound more like a motorsports radio call
    - slight overdrive
    - trim silence from both ends
    - normalize
    - downsample to 22.05KHz to match existing CrewChief format (optional)
    - ensure single channel
    Note that noise is not added since the CrewChief overlays background noise separately.

    You are encouraged to modify these effects to suit your own preferences. Use `man sox`
    in a terminal to see full documentation.
    """

    sox_command: List[str] = [
        "sox",
        "-V1",
        "-q",
        input_file,
        output_file,
        # "gain",
        # "-3",
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
        "channels",
        "1",
        "rate",
        "22050",
    ]

    try:
        subprocess.run(sox_command, check=True)
    except subprocess.CalledProcessError as e:
        logging.error(f"An error occurred: {e}")
        # TODO: raise the error for the caller


def is_invalid_wav_simple(file_path: str, tts_text: str) -> bool:
    """
    Use a simplistic check on the size, duration, and amount of silence in
    a xtts-created .wav file to determine if it is valid.
    Return False if the caller should regenerate this file (ie, try again to make a clean file).
    """
    is_invalid = (
        detect_excess_silence(
            file_path=file_path, silence_threshold=0.36 if len(tts_text) < 30 else 0.6
        )
        or detect_invalid_filesize(file_path)
        or detect_invalid_audio_duration(file_path=file_path, tts_text=tts_text)
    )

    if is_invalid:
        logging.warning(f"Invalid .wav file detected (simple check): {file_path}")

    return is_invalid


def is_invalid_wav_xtts_integrity(
    file_path: str, xtts_integrity_threshold: float = 0.9
) -> bool:
    """
    Use the xtts-integrity ML model to perform the .wav file validity check.
    Return False if the caller should regenerate this file (ie, try again to make a clean file).
    """
    model = init_xtts_integrity_model()
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    transform = InferenceAudioTransform()

    wav_files = [file_path]
    inference_dataset = AudioInferenceDataset(wav_files, transform=transform)
    inference_loader = DataLoader(inference_dataset, batch_size=48, shuffle=False)

    valid_files, invalid_files = run_inference(
        # note that threshold here can be lowered to allow lower-confidence
        # files to be accepted, which will reduce the amount of regeneration
        # at the cost of more audio artifacts slipping through
        model,
        inference_loader,
        device,
        threshold=xtts_integrity_threshold,
    )

    is_invalid = len(invalid_files) > 0

    if is_invalid:
        if len(invalid_files) < 1:
            logging.error(
                f"Error: Something unexpected went wrong when using xtts-integrity for file {file_path}"
            )
            return False

        score = invalid_files[0][1]
        logging.warning(
            f"Invalid .wav file detected: {file_path} with score {score:.2f}"
        )

    else:
        score = valid_files[0][1]
        logging.info(
            f"xtts_integrity validity check passed for {file_path} with score {score:.2f}"
        )

    return is_invalid


def is_invalid_wav_file(
    file_path: str,
    tts_text: str,
    use_xtts_integrity: bool = True,
    xtts_integrity_threshold: Optional[float] = None,
) -> bool:
    """
    Acceptance criteria for a valid file:
    - no periods of silence longer than x seconds
    - not longer than expected based on the input text
    - file size is not over x MB
    - audio duration not over x seconds
    - not materially longer than its other variants
    - no weird artifacts

    Return False if the caller should regenerate this file (ie, try again to make a clean file)
    """
    is_invalid = (
        is_invalid_wav_xtts_integrity(
            file_path, xtts_integrity_threshold=xtts_integrity_threshold
        )
        if (use_xtts_integrity and xtts_integrity_threshold is not None)
        else is_invalid_wav_simple(file_path=file_path, tts_text=tts_text)
    )

    return is_invalid


def detect_invalid_audio_duration(file_path: str, tts_text: str) -> bool:
    """
    Returns true if the audio duration is too long for the given text, based on
    the number of characters in the text and a rough estimate of speaking rate.
    """

    # generous estimate of speaking rate in characters per second
    speaking_rate = 3
    minimum_expected_duration = 1.0

    # calculate the expected duration based on the text
    expected_duration = len(tts_text) / speaking_rate + minimum_expected_duration

    # get the actual duration of the audio file
    audio_info = torchaudio.info(file_path)
    actual_duration = audio_info.num_frames / audio_info.sample_rate

    if actual_duration > expected_duration:
        logging.warning(
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
        logging.warning(f"Invalid file size detected. File too large: {file_path}")
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
                    logging.warning(
                        f"Excess silence detected in file {file_path}: {silence_duration:.2f} seconds"
                    )
                    return True

    except subprocess.CalledProcessError as e:
        logging.error(f"Error processing file {file_path}: {e}")
        return False

    return False


@lru_cache(maxsize=None)
def init_xtts_model(
    cpu_only: bool = False, use_deepspeed: bool = True, use_xtts_integrity: bool = True
) -> Any:
    """
    Initialize the xtts and xtts-integrity models. This function is cached, so it will only run
    once, and the model will be reused for all subsequent calls.
    """
    logging.info("xtts - Loading model...")

    # this model path is based on the Docker container's filesystem, so there should
    # be no need to change this unless the corresponding Dockerfile section changes
    model_path = (
        "/root/.local/share/tts/tts_models--multilingual--multi-dataset--xtts_v2"
    )
    config = XttsConfig()
    config.load_json(f"{model_path}/config.json")
    xtts_model = Xtts.init_from_config(config)
    xtts_model.load_checkpoint(
        config,
        checkpoint_dir=model_path,
        use_deepspeed=use_deepspeed,
    )
    xtts_model.cuda() if not cpu_only else xtts_model.cpu()

    if use_xtts_integrity:
        init_xtts_integrity_model()

    return xtts_model


@lru_cache(maxsize=None)
def init_xtts_integrity_model() -> Any:
    """
    Initialize the xtts-integrity model. This function is cached, so it will only run
    once, and the model will be reused for all subsequent calls.
    """
    logging.info("xtts_integrity - Loading model...")

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model_path = "/app/xtts-integrity/checkpoints/xtts-integrity-20241112.pth"
    xtts_integrity_model = load_model(model_path, device)

    return xtts_integrity_model


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
    logging.info("xtts - Computing speaker latents...")
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
    max_invalid_attempts: int = 30,
    use_xtts_integrity=True,
    xtts_integrity_threshold: Optional[float] = None,
):
    """
    Create a .wav file based on the input text and the reference speaker's voice.
    """

    # until the output passes the is_invalid_wav_file check, keep trying up to this many times
    for attempt_idx in range(max_invalid_attempts):
        was_generated = generate_speech_coqui_xtts(
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

        if was_generated and is_invalid_wav_file(
            file_path=file_path,
            tts_text=text,
            use_xtts_integrity=use_xtts_integrity,
            xtts_integrity_threshold=xtts_integrity_threshold,
        ):
            # skip the invalid file check if the file already existed from a previous run
            logging.info(f"Regenerating invalid .wav file: {output_filename}")

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
            # the audio file appears valid, so exit the regeneration loop
            break

    else:
        logging.error(
            f"Failed to generate a valid .wav file from the text '{text}' after {max_invalid_attempts} attempts: {output_filename}"
        )


def generate_speech_coqui_xtts(
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
) -> bool:
    """
    Generate speech using the Coqui TTS framework and the multilingual xtts model.
    See README.md for more details on Coqui.
    Returns True if the file was generated, False if it already existed and was skipped.
    # TODO: refactor, the file existence check should not be in this function
    """
    full_raw_filename = f"{output_path}/{output_filename}.raw.wav"
    full_output_filename = f"{output_path}/{output_filename}.wav"

    # immediately skip generating this file if it already exists (unless asked to overwrite)
    file_exists = os.path.isfile(full_output_filename) or os.path.isfile(
        full_raw_filename
    )
    if file_exists and not overwrite:
        logging.info(f"File exists, skipping: {full_output_filename}")
        return False

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

    logging.info(f"Audio file created: {full_output_filename}")
    return True


@dataclass
class ReplacementRule:
    regex: str
    replacement: str
    probability: float = (
        1.0  # Probability to apply the replacement, 1.0 means always apply
    )


def prepare_replacement_rules(args: argparse.Namespace) -> None:
    """Prepare text replacement rules"""
    args.replacement_rules = (
        []
        if args.disable_text_replacements
        else generate_replacement_rules(args.your_name)
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
            logging.info(
                f"Replacing '{rule.regex}' with '{rule.replacement}' in '{text}'"
            )
            text = re.sub(rule.regex, rule.replacement, text)
            logging.info(f"New value is: {text}")
    return text


def prepare_arguments() -> argparse.Namespace:
    """Parse command-line arguments and prepare any derived values."""
    args = parse_arguments()
    args.voicepack_base_dir = f"{args.output_audio_dir}/{args.voice_name}"
    args.tts_args = {
        "speed": args.xtts_speed,
        "temperature": random.uniform(0.2, 0.3),
        "reference_speaker_wav_paths": glob.glob(
            f"{args.baseline_audio_dir}/{args.voice_name}/*.wav"
        ),
        "overwrite": args.overwrite,
        "enable_audio_effects": not args.disable_audio_effects,
        "cpu_only": args.cpu_only,
        "use_deepspeed": (not args.disable_deepspeed) and (not args.cpu_only),
        "keep_invalid_files": args.keep_invalid_files,
        "max_invalid_attempts": args.max_invalid_attempts,
        "use_xtts_integrity": True if not args.simple_validity_check else False,
        "xtts_integrity_threshold": args.xtts_integrity_threshold,
    }
    return args


def setup_directories_and_files(args: argparse.Namespace) -> None:
    """Create necessary directories and write attribution and instruction files."""
    os.makedirs(args.voicepack_base_dir, exist_ok=True)

    write_attribution_file(args)
    write_installation_instructions(args)


def write_attribution_file(args: argparse.Namespace) -> None:
    """Write the attribution file."""
    attribution_filename = os.path.join(args.voicepack_base_dir, "CREATED_BY.txt")

    attribution_text = (
        "This voice pack was created using crew-chief-autovoicepack\n"
        "(https://github.com/cktlco/crew-chief-autovoicepack)\n\n"
        "...for use with the venerable virtual race engineer application CrewChief\n"
        "(https://thecrewchief.org/)\n"
        "(https://gitlab.com/mr_belowski/CrewChiefV4)\n\n\n"
    )

    # Add the rest of the args to the end in a key/value format
    attribution_text += "Configuration:\n\n"
    for key, value in vars(args).items():
        if key != "tts_args":  # only include user-specified arguments
            attribution_text += f"{key}: {value}\n"

    with open(attribution_filename, "w", encoding="utf-8") as f:
        f.write(attribution_text)
    logging.info(
        f"Attribution file written to {attribution_filename} for voicepack '{args.voice_name}' version {args.voicepack_version}'."
    )


def write_installation_instructions(args: argparse.Namespace) -> None:
    """Write the installation instructions file"""
    instructions_filename = f"{args.voicepack_base_dir}/INSTALLATION_INSTRUCTIONS.txt"
    instructions_text = (
        "To add this voice pack to CrewChief 4.18.4.0 or similar:\n\n"
        "1. From the CrewChief menu bar, select `File -> Open voice files folder`\n\n"
        "2. This will open a File Explorer window to a location such as:\n"
        "`C:\\Users\\YOUR_NAME\\AppData\\Local\\CrewChiefV4\\Sounds`\n\n"
        "3. In this folder, you will see a folder called `alt`\n\n"
        "4. Copy the main `{voice_name}` folder from the voice pack into the `alt` folder\n\n"
        "5. Confirm that you now have a folder called `...\\CrewChiefV4\\Sounds\\alt\\{voice_name}`\n\n"
        "6. Make sure to manually move the entire radio check folder at `...\\alt\\{voice_name}\\radio_check_{voice_name}` to `...\\CrewChiefV4\\Sounds\\voice\\radio_check_{voice_name}`\n\n"
        "7. Restart CrewChief and you will see `{voice_name}` in the dropdown list on the far right\n\n"
        "8. CrewChief will prompt you to restart again, and you should hear {voice_name} answer the radio check alongside your spotter.\n\n"
        "9. All done! Give Jim a well-deserved rest and enjoy frustrating a new engineer with your driving.\n\n"
        "To remove, 1) swap back to Jim in the CrewChief UI.  2) delete the `{voice_name}` folder from `...\\CrewChiefV4\\Sounds\\alt`. 3) delete the `radio_check_{voice_name}` folder from `...\\CrewChiefV4\\Sounds\\voice`.\n"
    )
    with open(instructions_filename, "w") as f:
        f.write(instructions_text.format(voice_name=args.voice_name))
    logging.info(f"Installation instructions written to {instructions_filename}.")


def process_phrase_inventory(args: argparse.Namespace) -> None:
    """Load and process the phrase inventory, generating audio files"""
    entries = parse_phrase_inventory(args.phrase_inventory)

    if not entries:
        logging.error("No entries found in the phrase inventory. Exiting.")
        return

    prepare_replacement_rules(args)

    if not args.original_inventory_order:
        random.shuffle(entries)

    # Expecting this many .wav files at the end
    total_wav_files = len(entries) * (1 + args.variation_count)

    start_time = time.time()
    last_update_time = start_time
    next_update_interval = args.progress_check_interval

    # Get the initial count of existing .wav files
    initial_wav_count = count_wav_files_in_tree(args.voicepack_base_dir)

    for entry_idx, entry in enumerate(entries, 1):
        logging.info(
            f"Considering phrase {entry_idx} - '{entry.subtitle}' -> '{entry.text_for_tts}'"
        )

        process_phrase_entry(entry, args)

        # Recount .wav files if it's time to update progress
        current_time = time.time()
        elapsed_since_last_update = current_time - last_update_time

        if elapsed_since_last_update >= next_update_interval:
            log_progress_string(
                args.voicepack_base_dir, start_time, total_wav_files, initial_wav_count
            )
            last_update_time = current_time

    # Final progress update after processing all entries
    log_progress_string(
        args.voicepack_base_dir, start_time, total_wav_files, initial_wav_count
    )

    logging.info(f"All entries in {args.phrase_inventory} have been generated.")
    generate_subtitle_files(entries, args)


def log_progress_string(
    voicepack_base_dir: str,
    start_time: float,
    total_wav_files: int,
    initial_wav_count: int,
):
    wav_files_in_dir = count_wav_files_in_tree(voicepack_base_dir)
    wav_files_created = wav_files_in_dir - initial_wav_count
    progress = progress_string(
        current_total=wav_files_in_dir,
        total=total_wav_files,
        current_created=wav_files_created,
        start_time=start_time,
    )
    logging.info(progress)


def progress_string(
    current_total: int, total: int, current_created: int, start_time: float
) -> str:
    """
    Generate a formatted string showing the progress of the audio generation process.

    Example output:
    Progress:   29.8% [==>       ] 2721/9145 phrases, 4.9 phrases/sec, ETA 0h 26m
    """
    percentage = (current_total / total) * 100 if total > 0 else 100
    bar_length = 10
    filled_length = (
        int(bar_length * current_total // total) if total > 0 else bar_length
    )

    if filled_length >= bar_length:
        bar = "=" * bar_length
    else:
        bar = "=" * filled_length + ">" + " " * (bar_length - filled_length - 1)

    elapsed_time = time.time() - start_time
    phrases_per_sec = current_created / elapsed_time if elapsed_time > 0 else 0
    remaining_created = total - current_created
    eta_sec = (
        remaining_created / phrases_per_sec if phrases_per_sec > 0 else float("inf")
    )
    eta_hours = int(eta_sec // 3600)
    eta_minutes = int((eta_sec % 3600) // 60)
    eta_string = (
        f"ETA {eta_hours}h {eta_minutes}m" if eta_sec != float("inf") else "ETA Unknown"
    )

    progress = (
        f"Progress: {percentage:4.1f}% [{bar}] {current_total}/{total} phrases, "
        f"{phrases_per_sec:.1f} phrases/sec, {eta_string}"
    )
    return progress


def count_wav_files_in_tree(directory: str) -> int:
    """Count all .wav files in the directory tree under the given directory"""
    return len(glob.glob(os.path.join(directory, "**", "*.wav"), recursive=True))


def process_phrase_entry(entry: CrewChiefAudioFile, args: argparse.Namespace) -> None:
    """Process a single phrase inventory entry"""
    entry.text_for_tts_filtered = (
        entry.text_for_tts
        if args.disable_text_replacements
        else apply_replacements(entry.text_for_tts, args.replacement_rules)
    ).replace("YOUR_NAME", args.your_name)

    entry.audio_path_filtered = entry.audio_path.replace("YOUR_NAME", args.your_name)
    entry.subtitle_filtered = entry.subtitle.replace("YOUR_NAME", args.your_name)

    for variant_id in range(0, args.variation_count + 1):
        variant_filename = generate_variant_filename(
            entry, variant_id, args.variation_count
        )
        generate_speech(
            **args.tts_args,
            text=entry.text_for_tts_filtered,
            output_path=f"{args.voicepack_base_dir}{entry.audio_path_filtered}",
            output_filename=variant_filename,
        )


def generate_variant_filename(
    entry: CrewChiefAudioFile, variant_id: int, variation_count: int
) -> str:
    """Generate a filename for a variant of a phrase."""
    if variation_count == 0:
        return entry.audio_filename
    else:
        variant_tag = chr(variant_id + ord("a"))  # a-z
        return f"{entry.audio_filename}-{variant_tag}"


def generate_subtitle_files(
    entries: List[CrewChiefAudioFile], args: argparse.Namespace
) -> None:
    """Generate subtitles.csv files for each subfolder."""
    subtitle_entries = group_entries_by_path(entries)

    for subtitle_path, entry_details in subtitle_entries.items():
        subtitle_filename = f"{args.voicepack_base_dir}{subtitle_path}/subtitles.csv"

        if not args.overwrite and os.path.isfile(subtitle_filename):
            logging.debug(f"Skipping subtitles.csv since it exists at {subtitle_path}")
        else:
            logging.debug(f"Creating subtitles.csv for {subtitle_path}")
            write_subtitle_file(subtitle_filename, entry_details, args.variation_count)


def group_entries_by_path(entries: List[CrewChiefAudioFile]) -> dict:
    """Group together phrase_inventory.csv rows from the same folder."""
    subtitle_entries: dict[Any, Any] = {}
    for entry in entries:
        if entry.audio_path_filtered not in subtitle_entries:
            subtitle_entries[entry.audio_path_filtered] = []
        subtitle_entries[entry.audio_path_filtered].append(
            (entry.audio_filename, entry.subtitle_filtered)
        )
    return subtitle_entries


def write_subtitle_file(
    filename: str, entry_details: List[tuple], variation_count: int
) -> None:
    """Create a subtitles.csv file at the given path, using the existing CrewChief convention."""
    with open(filename, "w") as f:
        for audio_filename, subtitle in entry_details:
            for variant_id in range(0, variation_count + 1):
                variant_tag = chr(variant_id + ord("a"))
                f.write(f'{audio_filename}-{variant_tag}.wav,"{subtitle}"\n')


def generate_radio_checks(args: argparse.Namespace) -> None:
    """Generate the radio check audio clips"""
    logging.info("Generating radio check audio clips...")
    voice_name_tts = args.voice_name_tts or args.voice_name
    radio_check_phrases = (
        [args.radio_check_tts_text]
        if args.radio_check_tts_text
        else get_radio_check_phrases(voice_name_tts)
    )

    for radio_check_idx, radio_check_phrase in enumerate(radio_check_phrases, 1):
        logging.info(
            f"Considering radio check audio clip {radio_check_idx} - {radio_check_phrase}..."
        )
        generate_speech(
            **args.tts_args,
            text=radio_check_phrase,
            output_path=f"{args.voicepack_base_dir}/radio_check_{args.voice_name}/test",
            output_filename=f"{radio_check_idx}",
        )
    logging.info("All radio check audio clips have been generated.")


def get_radio_check_phrases(voice_name_tts: str) -> List[str]:
    """Return a list of radio check phrases"""
    return [
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


def main():
    """The main entry point for the script."""
    args = prepare_arguments()
    setup_directories_and_files(args)

    if not args.skip_inventory:
        process_phrase_inventory(args)

    if not args.skip_radio_check:
        generate_radio_checks(args)

    # TODO: add progress bar in this format:
    #    phrase (truncated)...      50%[========================>                         ] 56/30,000 phrases, x phrases per second    ETA 12h 14m
    #    using a "slow" check which counts all the .wav files in the directory tree every 30-60 seconds
    #    and compares it to the total expected number of phrases to generate

    # TODO: generate subtitles.csv for the radio_check folder

    # TODO: generate audio for the driver_names folder, optionally either including all the CrewChief names
    #       (from a static JSON file in this repo) or just a single name based on args.your_name with a dozen variants
    # if not args.skip_driver_names:
    #     generate_driver_names(args)

    # TODO: generate optional spotter audio pack
    # if not args.skip_spotter:
    #     generate_spotter(args)

    logging.info("Voice pack generation complete.")


if __name__ == "__main__":
    logging.info("Starting...")
    main()
