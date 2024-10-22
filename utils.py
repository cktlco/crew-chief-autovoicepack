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
            row_fields = row[:4]  # only consider the first 4 fields
            audio_path_windows, audio_filename_with_ext, subtitle, text_for_tts = (
                row_fields
            )

            audio_filename = audio_filename_with_ext.replace(".wav", "")
            # swap from backslashes (Windows) to forward slashes (Linux)
            audio_path = audio_path_windows.replace("\\", "/")

            # put the csv file data into a more friendly data structure
            entries.append(
                CrewChiefAudioFile(audio_path, audio_filename, subtitle, text_for_tts)
            )

    return entries
