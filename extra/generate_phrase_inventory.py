# Build a crew-chief-autovoicepack phrase inventory CSV file from scratch by
# searching through CrewChief wav file folders and collecting subtitles.csv data.
#
# Note the final CSV file will need manual edits to add and remove rows in order
# to match with the official version used in the git repo.

from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path
from typing import Dict, List, Sequence


def parse_arguments(argv: Sequence[str]) -> argparse.Namespace:
    """ Parse command-line arguments """
    default_input = (
        Path.home() / "AppData" / "Local" / "CrewChiefV4" / "sounds" / "voice"
    )
    parser = argparse.ArgumentParser(
        description="Produce an inventory of wav files and optional subtitles"
    )
    parser.add_argument(
        "--input-dir",
        type=Path,
        default=Path(default_input),
        help=r"Root directory containing CrewChief 'voice' folders. Defaults to: '%USERPROFILE%\AppData\Local\CrewChiefV4\sounds\voice'",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("phrase_inventory.csv"),
        help="Path for generated phrase inventory CSV file",
    )
    return parser.parse_args(argv)


def read_subtitles(sub_file: Path) -> Dict[str, str]:
    """ Read subtitles.csv, returning mapping of filename to subtitle """
    mapping: Dict[str, str] = {}

    print(f"  loading subtitles from {sub_file}")
    encoding = "utf-8-sig"  # Excel for Windows encoding
    with sub_file.open(newline="", encoding=encoding) as fh:
        reader = csv.reader(fh)
        rows = list(reader)

    # accept subtitles.csv header if present
    header = rows[0]
    data_rows = rows[1:] if any(cell.lower() == "filename" for cell in header) else rows

    for row in data_rows:
        if not row:
            continue
        filename, subtitle = row[0].strip(), row[1].strip()
        mapping[filename] = subtitle
    return mapping


def gather_rows(root: Path) -> List[Dict[str, str]]:
    """ Walk input dir collecting wav info and subtitles.csv data """
    if not root.is_dir():
        raise NotADirectoryError(f"{root} is not a directory")

    rows: List[Dict[str, str]] = []
    print(f"Scanning {root}")

    # track which spotter_* directory (if any) has been accepted
    spotter_selected: str | None = None

    # iterate through immediate & nested subdirectories
    for folder in (p for p in root.rglob("*") if p.is_dir()):
        rel_parts = folder.relative_to(root).parts
        if rel_parts:
            top = rel_parts[0]
            if top.startswith("spotter_"):
                if spotter_selected is None:
                    spotter_selected = top  # keep the first spotter_* encountered
                elif top != spotter_selected:
                    continue  # skip other spotter_* directories

        wav_files = sorted(folder.glob("*.wav"))
        if not wav_files:
            continue

        print(f"- found {len(wav_files):4d} wav files in {folder.relative_to(root)}")

        sub_file = folder / "subtitles.csv"
        subtitles = read_subtitles(sub_file) if sub_file.exists() else {}

        for wav in wav_files:
            rel_path = f"\\{folder.relative_to(root)}".replace("/", "\\")
            subtitle = subtitles.get(wav.name, "")
            rows.append(
                {
                    "audio_path": rel_path,
                    "audio_filename": wav.name,
                    "subtitle": subtitle,
                    "text_for_tts": subtitle
                }
            )
    return rows


def write_csv(rows: List[Dict[str, str]], out_file: Path) -> None:
    """ Write collected rows to CSV file """
    print(f"Writing {len(rows)} rows to {out_file}")
    with out_file.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(
            fh,
            fieldnames=["audio_path", "audio_filename", "subtitle", "text_for_tts"],
        )
        writer.writeheader()
        writer.writerows(rows)
    print("CSV file written")


def main(argv: Sequence[str] | None = None) -> None:
    """ Script entry point """
    args = parse_arguments(argv or sys.argv[1:])
    rows = gather_rows(args.input_dir)
    write_csv(rows, args.output)


if __name__ == "__main__":
    main()
