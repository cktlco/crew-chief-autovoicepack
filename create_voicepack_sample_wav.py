import csv
import random
import subprocess
import os

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
        "Shit, we won, wow"
    ],
    [
        "The safety car's out",
        "Maximize every lap, let's salvage what we can",
        "You're 2 tenths off your best in sector 3",
        "That's the fastest lap",
        "Come on, track limits, that's another cut",
        "Heads up, we're going green",
        "Push now, we can catch this guy",
        "The car behind is pitting"
    ],
    [
        "The safety car's out, yellow flag",
        "Push now, we can catch up here",
        "Your tyre temps are good",
        "Keep it nice and smooth, come on, let the race come to us",
        "Green flag, all clear",
        "That's the fastest lap",
        "Looks like P5's gone off in",
        "The car behind is pitting"
    ],
    [
        "Green flag sector 3",
        "Keep piling on the pressure, he'll make a mistake",
        "You're quickest in sector 3",
        "That's the fastest lap",
        "Stay close, wait for him to crack",
        "Come on, track limits, that's another cut",
        "The car behind is pitting",
        "The safety car's out"
    ],
    [
        "Heads up, we're going green",
        "Don't be intimidated, keep him behind you",
        "Yellow flag, stay sharp",
        "You're 2 tenths off your best in sector 3",
        "That's the fastest lap",
        "Maximize every lap, let's salvage what we can",
        "Push now, we can catch up here",
        "The car behind is pitting"
    ],
    [
        "Yellow flag, sector 3",
        "Push now, we can catch up here",
        "Your brakes look good from here",
        "Maximize every lap, let's salvage what we can",
        "Green flag, all clear",
        "That's the fastest lap",
        "There's a car leaving the pits, be careful",
        "The car behind is pitting"
    ],
    [
        "The safety car's out, yellow flag",
        "Keep it nice and smooth, come on, let the race come to us",
        "You're fastest in sector 3",
        "That's the fastest lap",
        "Green flag, all clear",
        "Push now, we can catch this guy",
        "Your tyre temps are good",
        "The car behind is pitting"
    ],
    [
        "Heads up, we're going green",
        "Don't let this guy intimidate you",
        "You're 2 tenths off your best in sector 3",
        "Yellow flag, stay sharp",
        "Keep piling on the pressure, he'll make a mistake",
        "That's the fastest lap",
        "Green flag sector 3",
        "The car behind is pitting"
    ],
    [
        "Green flag, all clear",
        "Push now, we can catch this guy",
        "You're fastest in sector 3",
        "That's the fastest lap",
        "Yellow flag, sector 3",
        "Stay close, wait for him to crack",
        "Keep it nice and smooth, come on, let the race come to us",
        "The safety car's out"
    ],
    [
        "The safety car's out, yellow flag",
        "Keep it nice and smooth, come on, let the race come to us",
        "You're quickest in sector 3",
        "That's the fastest lap",
        "Green flag, all clear",
        "Push now, we can catch this guy",
        "There's a car leaving the pits, be careful",
        "The car behind is pitting"
    ],
    [
        "Heads up, we're going green",
        "Don't be intimidated, keep him behind you",
        "Yellow flag, stay sharp",
        "You're 2 tenths off your best in sector 3",
        "That's the fastest lap",
        "Maximize every lap, let's salvage what we can",
        "Push now, we can catch up here",
        "The car behind is pitting"
    ],
    [
        "Yellow flag, sector 3",
        "Push now, we can catch up here",
        "Your brakes look good from here",
        "Maximize every lap, let's salvage what we can",
        "Green flag, all clear",
        "That's the fastest lap",
        "There's a car leaving the pits, be careful",
        "The car behind is pitting"
    ],
    [
        "Green flag sector 3",
        "Keep piling on the pressure, he'll make a mistake",
        "You're quickest in sector 3",
        "That's the fastest lap",
        "Stay close, wait for him to crack",
        "Come on, track limits, that's another cut",
        "The car behind is pitting",
        "The safety car's out"
    ],
    [
        "The safety car's out",
        "Maximize every lap, let's salvage what we can",
        "You're 2 tenths off your best in sector 3",
        "That's the fastest lap",
        "Come on, track limits, that's another cut",
        "Heads up, we're going green",
        "Push now, we can catch this guy",
        "The car behind is pitting"
    ]
]


# Path to the CSV file
csv_file_path = 'phrase_inventory.csv'
names = ["Ana", "Bart", "Blake", "David", "Don", "Hiroshi", "Jamal", "Luis", "Madeline", "Norm", "Paul", "Rajan", "Sally", "Shannon"]

# Function to get matching audio paths for a single list of phrases
def get_matching_audio_files(phrases_to_match, random_choice=False):
    matching_audio_files = []

    with open(csv_file_path, mode='r', newline='') as file:
        reader = csv.DictReader(file)
        rows = list(reader)  # Load all rows into memory to avoid issues with file pointer resetting

        for phrase in phrases_to_match:
            matching_rows = [
                f"{row['audio_path']}\\{row['audio_filename']}"
                for row in rows
                if phrase.strip().lower() == row['subtitle'].strip().lower()
            ]
            if matching_rows:
                if random_choice:
                    selected_audio = random.choice(matching_rows)
                else:
                    selected_audio = matching_rows[0]
                matching_audio_files.append(selected_audio)

    return matching_audio_files

# Function to concatenate audio files with 500ms of silence between them
def concatenate_audio_files(name, audio_files):
    temp_list_path = f"temp_{name}.txt"
    with open(temp_list_path, 'w') as f:
        for audio_file in audio_files:
            adjusted_audio_file = audio_file.replace("\\", "/")
            adj_audio_file_without_ext = os.path.splitext(adjusted_audio_file)[0]
            full_path = f"output/{name}{adj_audio_file_without_ext}-a.wav"
            f.write(f"file '{full_path}'\n")
            f.write("file 'silence.wav'\n")  # Add 500ms of silence between files

    # Output file name
    output_file = f"output/{name}/{name}_speech_demo.wav"

    # Use ffmpeg to concatenate
    subprocess.run([
        "ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", temp_list_path, "-c", "copy", output_file
    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    # Cleanup temporary list file
    os.remove(temp_list_path)

    print(f"Created voice pack sample .wav file for {name} at {output_file}")

# Create a 300ms silence.wav file if it doesn't exist
if not os.path.exists("silence.wav"):
    subprocess.run([
        "ffmpeg", "-f", "lavfi", "-i", "anullsrc=r=44100:cl=stereo", "-t", "0.3", "silence.wav"
    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

# Iterate over each list of phrases and concatenate audio files for each name
for i, (phrases_to_match, name) in enumerate(zip(phrases_to_match_list, names)):
    matching_audio_files = get_matching_audio_files(phrases_to_match, random_choice=True)

    if matching_audio_files:
        concatenate_audio_files(name, matching_audio_files)
    else:
        print(f"No matching audio files for {name}")

os.remove("silence.wav")

print("All voice pack sample .wav files created.")