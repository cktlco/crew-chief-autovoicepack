from dataclasses import dataclass
from typing import List
import csv


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


def parse_phrase_inventory(
    inventory_file_path: str, convert_slashes: bool = True
) -> List[CrewChiefAudioFile]:
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
            row_fields = row[:4]  # only consider the first 4 fields
            audio_path_windows, audio_filename_with_ext, subtitle, text_for_tts = (
                row_fields
            )

            audio_filename = audio_filename_with_ext.replace(".wav", "")
            # swap from backslashes (Windows) to forward slashes (Linux)
            if convert_slashes:
                audio_path = audio_path_windows.replace("\\", "/")

            # put the csv file data into a more friendly data structure
            entries.append(
                CrewChiefAudioFile(audio_path, audio_filename, subtitle, text_for_tts)
            )

    return entries


def progress_string(
    current_total: int,
    total: int,
    start_time: float,
    current_time: float,
    previous_total: int,
    previous_time: float,
    initial_total: int,
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

    # Calculate phrases per second based on the difference since last update
    time_diff = current_time - previous_time
    phrases_diff = current_total - previous_total
    phrases_per_sec = phrases_diff / time_diff if time_diff > 0 else 0

    # If phrases_per_sec is zero, use cumulative average
    if phrases_per_sec <= 0:
        total_time = current_time - start_time
        phrases_diff = current_total - initial_total
        phrases_per_sec = phrases_diff / total_time if total_time > 0 else 0

    remaining_phrases = total - current_total
    eta_sec = (
        remaining_phrases / phrases_per_sec if phrases_per_sec > 0 else float("inf")
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
