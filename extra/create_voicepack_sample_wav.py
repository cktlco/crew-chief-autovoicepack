import csv
import random
import subprocess
import os

# self-contained utility script to create a sample .wav audio and .mp4 video
# file for each official voicepack name in the crew-chief-autovoicepack repository

# All 14 lists of phrases
phrases_to_match_list = [
    [
        "Heads up, we're going green",
        "Don't let this guy intimidate you",
        "You're fastest in sector 3",
        "Yellow flag, safety car is out",
        "Keep piling on the pressure, he'll make a mistake",
        "Green flag, all clear",
        "That's the fastest lap",
        "Shit, we won, wow",
    ],
    [
        "The safety car's out",
        "Maximize every lap, let's salvage what we can",
        "You're 2 tenths off your best in sector 3",
        "That's the fastest lap",
        "Come on, track limits, that's another cut",
        "Heads up, we're going green",
        "Push now, we can catch this guy",
        "The car behind is pitting",
    ],
    [
        "The safety car's out, yellow flag",
        "Push now, we can catch up here",
        "Your tyre temps are good",
        "Keep it nice and smooth, come on, let the race come to us",
        "Green flag, all clear",
        "That's the fastest lap",
        "Looks like P5's gone off in",
        "The car behind is pitting",
    ],
    [
        "Green flag sector 3",
        "Keep piling on the pressure, he'll make a mistake",
        "You're quickest in sector 3",
        "That's the fastest lap",
        "Stay close, wait for him to crack",
        "Come on, track limits, that's another cut",
        "The car behind is pitting",
        "The safety car's out",
    ],
    [
        "Heads up, we're going green",
        "Don't be intimidated, keep him behind you",
        "Yellow flag, stay sharp",
        "You're 2 tenths off your best in sector 3",
        "That's the fastest lap",
        "Maximize every lap, let's salvage what we can",
        "Push now, we can catch up here",
        "The car behind is pitting",
    ],
    [
        "Yellow flag, sector 3",
        "Push now, we can catch up here",
        "Your brakes look good from here",
        "Maximize every lap, let's salvage what we can",
        "Green flag, all clear",
        "That's the fastest lap",
        "There's a car leaving the pits, be careful",
        "The car behind is pitting",
    ],
    [
        "The safety car's out, yellow flag",
        "Keep it nice and smooth, come on, let the race come to us",
        "You're fastest in sector 3",
        "That's the fastest lap",
        "Green flag, all clear",
        "Push now, we can catch this guy",
        "Your tyre temps are good",
        "The car behind is pitting",
    ],
    [
        "Heads up, we're going green",
        "Don't let this guy intimidate you",
        "You're 2 tenths off your best in sector 3",
        "Yellow flag, stay sharp",
        "Keep piling on the pressure, he'll make a mistake",
        "That's the fastest lap",
        "Green flag sector 3",
        "The car behind is pitting",
    ],
    [
        "Green flag, all clear",
        "Push now, we can catch this guy",
        "You're fastest in sector 3",
        "That's the fastest lap",
        "Yellow flag, sector 3",
        "Stay close, wait for him to crack",
        "Keep it nice and smooth, come on, let the race come to us",
        "The safety car's out",
    ],
    [
        "The safety car's out, yellow flag",
        "Keep it nice and smooth, come on, let the race come to us",
        "You're quickest in sector 3",
        "That's the fastest lap",
        "Green flag, all clear",
        "Push now, we can catch this guy",
        "There's a car leaving the pits, be careful",
        "The car behind is pitting",
    ],
    [
        "Heads up, we're going green",
        "Don't be intimidated, keep him behind you",
        "Yellow flag, stay sharp",
        "You're 2 tenths off your best in sector 3",
        "That's the fastest lap",
        "Maximize every lap, let's salvage what we can",
        "Push now, we can catch up here",
        "The car behind is pitting",
    ],
    [
        "Yellow flag, sector 3",
        "Push now, we can catch up here",
        "Your brakes look good from here",
        "Maximize every lap, let's salvage what we can",
        "Green flag, all clear",
        "That's the fastest lap",
        "There's a car leaving the pits, be careful",
        "The car behind is pitting",
    ],
    [
        "Green flag sector 3",
        "Keep piling on the pressure, he'll make a mistake",
        "You're quickest in sector 3",
        "That's the fastest lap",
        "Stay close, wait for him to crack",
        "Come on, track limits, that's another cut",
        "The car behind is pitting",
        "The safety car's out",
    ],
    [
        "The safety car's out",
        "Maximize every lap, let's salvage what we can",
        "You're 2 tenths off your best in sector 3",
        "That's the fastest lap",
        "Come on, track limits, that's another cut",
        "Heads up, we're going green",
        "Push now, we can catch this guy",
        "The car behind is pitting",
    ],
]

# Path to the CSV file
csv_file_path = "../phrase_inventory.csv"
names = [
    "Ana",
    "Bart",
    "Blake",
    "David",
    "Don",
    "Hiroshi",
    "Jamal",
    "Luis",
    "Madeline",
    "Norm",
    "Paul",
    "Rajan",
    "Sally",
    "Shannon",
]


def convert_windows_to_unix_path(windows_path):
    return windows_path.replace("\\", "/")


def get_matching_audio_files(phrases_to_match, name, random_choice=False):
    matching_audio_files = []

    with open(csv_file_path, mode="r", newline="") as file:
        reader = csv.DictReader(file)
        rows = list(reader)

        for phrase in phrases_to_match:
            matching_rows = [
                convert_windows_to_unix_path(
                    f"output/{name}/{row['audio_path']}/{os.path.splitext(row['audio_filename'])[0]}-a.wav"
                )
                for row in rows
                if phrase.strip().lower() == row["subtitle"].strip().lower()
            ]
            if matching_rows:
                if random_choice:
                    selected_audio = random.choice(matching_rows)
                else:
                    selected_audio = matching_rows[0]
                matching_audio_files.append(selected_audio)

    return matching_audio_files


def reencode_audio_files(audio_files):
    reencoded_files = []
    for audio_file in audio_files:
        reencoded_file = f"{os.path.splitext(audio_file)[0]}_reencoded.wav"
        subprocess.run(
            [
                "ffmpeg",
                "-y",
                "-i",
                audio_file,
                "-c:a",
                "pcm_s16le",
                "-ar",
                "44100",
                "-ac",
                "2",
                "-fflags",
                "+genpts",
                reencoded_file,
            ],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        reencoded_files.append(reencoded_file)
    return reencoded_files


def calculate_subtitle_timings(audio_files, silence_duration):
    timings = []
    current_time = silence_duration  # Start timings after the initial silence

    for audio_file in audio_files:
        audio_duration = get_audio_duration(audio_file)
        start_time = current_time
        end_time = start_time + audio_duration
        timings.append((start_time, end_time))
        current_time = end_time + silence_duration

    return timings


def concatenate_audio_files_and_create_srt(name, audio_files, phrases):
    temp_list_path = f"temp_{name}.txt"
    srt_file_path = f"output/{name}/{name}_subtitles.srt"
    os.makedirs(f"output/{name}", exist_ok=True)

    silence_duration = 0.3  # Set silence duration to 300ms

    # Re-encode the audio files to ensure consistent format
    reencoded_files = reencode_audio_files(audio_files)

    # Calculate precise timings for subtitles
    timings = calculate_subtitle_timings(reencoded_files, silence_duration)

    with open(temp_list_path, "w") as f, open(srt_file_path, "w") as srt_file:
        # Prepend the initial silence
        f.write("file 'silence.wav'\n")

        for index, (audio_file, (start_time, end_time)) in enumerate(
            zip(reencoded_files, timings)
        ):
            full_path = convert_windows_to_unix_path(audio_file)
            f.write(f"file '{full_path}'\n")
            f.write("file 'silence.wav'\n")

            srt_file.write(f"{index + 1}\n")
            srt_file.write(f"{format_time(start_time)} --> {format_time(end_time)}\n")
            srt_file.write(f"{phrases[index]}\n\n")

    output_wav_file = f"output/{name}/{name}_speech_demo.wav"

    subprocess.run(
        [
            "ffmpeg",
            "-y",
            "-fflags",
            "+genpts",
            "-f",
            "concat",
            "-safe",
            "0",
            "-i",
            temp_list_path,
            "-c:a",
            "pcm_s16le",
            "-ar",
            "44100",
            "-ac",
            "2",
            output_wav_file,
        ],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

    os.remove(temp_list_path)

    print(f"Created voice pack sample .wav file for {name} at {output_wav_file}")

    create_mp4_with_subtitles(name, output_wav_file, srt_file_path)

    os.remove(srt_file_path)
    # Cleanup reencoded files
    for file in reencoded_files:
        os.remove(file)


def get_audio_duration(file_path):
    file_path = convert_windows_to_unix_path(file_path)

    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")

    result = subprocess.run(
        [
            "ffprobe",
            "-v",
            "error",
            "-show_entries",
            "format=duration",
            "-of",
            "default=noprint_wrappers=1:nokey=1",
            file_path,
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    duration = float(result.stdout.strip())
    return duration


def format_time(seconds):
    millis = int((seconds - int(seconds)) * 1000)
    time_str = f"{int(seconds // 3600):02}:{int((seconds % 3600) // 60):02}:{int(seconds % 60):02},{millis:03}"
    return time_str


def create_mp4_with_subtitles(name, wav_file, srt_file):
    image_path = f"resources/images/{name}.webp"
    output_mp4_file = f"output/{name}/{name}_speech_demo.mp4"

    subtitle_style = (
        "Fontsize=32,PrimaryColour=&HFFFFFF&,Alignment=2,MarginV=60,Outline=4,Karaoke=1"
    )

    subprocess.run(
        [
            "ffmpeg",
            "-loop",
            "1",
            "-y",
            "-i",
            image_path,
            "-i",
            wav_file,
            "-vf",
            f"subtitles={srt_file}:force_style='{subtitle_style}'",
            "-c:v",
            "libx264",
            "-c:a",
            "aac",
            "-strict",
            "experimental",
            "-b:a",
            "192k",
            "-shortest",
            output_mp4_file,
        ],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

    print(f"Created MP4 file with subtitles for {name} at {output_mp4_file}")


if not os.path.exists("silence.wav"):
    subprocess.run(
        [
            "ffmpeg",
            "-f",
            "lavfi",
            "-y",
            "-i",
            "anullsrc=r=44100:cl=stereo",
            "-t",
            "0.3",
            "silence.wav",
        ],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

for i, (phrases_to_match, name) in enumerate(zip(phrases_to_match_list, names)):
    matching_audio_files = get_matching_audio_files(
        phrases_to_match, name, random_choice=True
    )

    if matching_audio_files:
        concatenate_audio_files_and_create_srt(
            name, matching_audio_files, phrases_to_match
        )
    else:
        print(f"No matching audio files for {name}")

os.remove("silence.wav")

print("All voice pack sample .mp4 files created.")
