import os
from pprint import pprint
from typing import List
import re


def parse_filename_for_tts(filename: str) -> str:
    name, _ = os.path.splitext(filename)
    name = name.strip()

    # Replace leading zeros with "oh " if present
    def replace_leading_zeros(part: str) -> str:
        return re.sub(r"\b0(\d)", r"oh \1", part)

    if "point" in name:
        parts = name.split("point")
        if len(parts) == 2:
            second_part = replace_leading_zeros(parts[1])
            if "seconds" in second_part:
                second_part = second_part.replace("seconds", "-seconds")
            return f"{parts[0]}-point {second_part}".strip()
    elif "_" in name:
        if re.search(r"^\d+_\d+$", name):
            # Handle cases like "1_01" as "1 oh 1" if leading zero is present
            parts = name.split("_")
            second_part = replace_leading_zeros(parts[1])
            return f"{parts[0]} {second_part}".strip()
        elif re.search(r"_\d", name):
            # Convert underscore to " oh " for cases like "2_03"
            parts = name.split("_")
            return f"{parts[0]} oh {parts[1]}".strip()
        else:
            return name.replace("_", " ").strip()
    else:
        return name.strip()


def find_leaf_dirs_without_subtitles_csv(root_dir: str) -> None:
    for dirpath, dirnames, filenames in os.walk(root_dir):
        # Only consider leaf directories (no child directories)
        if not dirnames and "subtitles.csv" not in filenames:
            for filename in filenames:
                transcript = parse_filename_for_tts(dirpath.rsplit("/")[-1])
                print(f'"{dirpath}:{filename}","{transcript}"')
                # "\voice\codriver\cmp_into_corner_1_right_descriptive_rushed:16.wav","into hairpin right"


def compare_dirs(dir1: str, dir2: str) -> List[str]:
    """
    Compare two directory trees and return a list of paths that are in dir1 but not in dir2,
    excluding "subtitles.csv".

    :param dir1: Path to the first directory.
    :param dir2: Path to the second directory.
    :return: List of paths that are in dir1 but not in dir2.
    """
    exclude_file = "subtitles.csv"

    dir1_files = set()
    dir2_files = set()

    for root, _, files in os.walk(dir1):
        for file in files:
            if file != exclude_file:
                dir1_files.add(os.path.relpath(os.path.join(root, file), dir1))
        for subdir in os.listdir(root):
            if os.path.isdir(os.path.join(root, subdir)):
                dir1_files.add(os.path.relpath(os.path.join(root, subdir), dir1))

    for root, _, files in os.walk(dir2):
        for file in files:
            if file != exclude_file:
                dir2_files.add(os.path.relpath(os.path.join(root, file), dir2))
        for subdir in os.listdir(root):
            if os.path.isdir(os.path.join(root, subdir)):
                dir2_files.add(os.path.relpath(os.path.join(root, subdir), dir2))

    diff = list(dir1_files - dir2_files)
    diff.sort()  # Sort the result for easier readability
    return diff


# Usage
root_directory = "original_sounds/voice"
# find_leaf_dirs_without_subtitles_csv(root_directory)
pprint(compare_dirs(root_directory, "output/mercury/voice"))
