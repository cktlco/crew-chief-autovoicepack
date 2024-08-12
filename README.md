### Capabilities
- automatically generate a full CrewChief voicepack from 30 seconds of any voice
- supports all CrewChief phrases and sims (Assetto Corsa, ACC, iRacing, etc.)
- natural-sounding speech using free software
- no-cost, unlimited usage, runs locally on your PC
- easily replace original CrewChief commentary with fully custom phrases
- use ANY voice you want: your own, a friend, a favorite celebrity
- optionally import high-quality professional voices from ElevenLabs.io (for free)
- generate voice packs in any language (requires machine/human text translation)
- fast -- 1-2 hours for tens of thousands of audio files (RTX 3090)
- runs on any hardware, Windows/Mac/Linux, CPU-only or CUDA GPU
- elegantly packaged as a ready-to-use Docker image
- friendly Python code you are encouraged to tweak
- remove (or introduce!) swear words and regional language quirks


### Video demonstration
TBD


### Download new voicepacks created by crew-chief-autovoicepack
Try it yourself, or download one of these ready-to-go, full-fat replacement voices for CrewChief. Unzip and copy files as mentioned below.
- Sally
- Don
- Blake
- Shannon
- Rajan
- Jamal
- David
- Ana
- Norm
- Brad
- Paul
- Hiroshi
- Luis
- Madeline


### Known Issues
- generated voices do not exactly match the original speaker's voice
- poor or incorrect TTS pronounciations (driver names, corner names, etc.)
- occasional garbled or corrupt audio (a few percent of the total)
- speed/pace is not easily adjustable (i.e. "rushed" CrewChief phrases are not rushed)
- minor: may adopt incorrect accent or diminish input accent on certain TTS phrases
- minor: emotional inflection is worse than a human voice actor
- minor: rarely, may fail applying audio effects and leave the interim x.raw.wav file and no x.wav file
- minor: voicepack name must use ASCII characters (e.g. UTF-8 chars like é, ñ, are not supported)
- minor: "sweary" phrases are not denoted with `_sweary` prefix in the filename


### Possible Future Improvements
- Incorporate RVC (Real Voice Cloning) to better match the original speaker's voice -- this would take the TTS generated audio and post-process it to sound even more like the original. Could also be applied to the original CrewChief "Jim" voice pack audio to retain the emotional inflection and pacing (though unavoidably inheriting the regional jargon and matey-ness).



### Common Task: Generate a new voice pack
The only required software on your machine is a working installation of Docker.

Windows or Mac users can install this via [Docker Desktop](https://docs.docker.com/desktop/), while Linux users can install Docker via their OS package manager or the official installation instructions .

For Docker Desktop users -- note that all instructions here will be performed via the command line, so ensure the basic Docker hello-world tests work before proceeding.

1. Download the crew-chief-autovoicepack Docker image with:
```
docker pull crew-chief-autovoicepack:v0.1
```
You can confirm this step worked with `docker image list crew-chief-autovoicepack`.

2. Start a container to run the downloaded image

- Example (Linux): `docker run -it --rm --gpus all --name crew-chief-autovoicepack -v ~/crew-chief-autovoicepack/output:/app/output crew-chief-autovoicepack:v0.1`

- Example (Windows): `docker run -it --rm --gpus all --name crew-chief-autovoicepack -v C:\Users\myuser\Desktop\crew-chief-autovoicepack\output:/app/output crew-chief-autovoicepack:v0.1`

Important:
- Change the mounted folder path above to a location on your local machine where you want the generated audio files to be saved.
- Remember to include the `--gpus all` parameter if you have a CUDA-capable NVIDIA GPU and want to use it for the voice pack generation. If you don't have a GPU, you can run in CPU-only mode, which is slower but still works fine.

`docker run -it ...` will create a new container and drop you into a bash prompt:
```bash
crew-chief-autovoicepack > 
```

From there, run the `generate_voice_pack.py` script to start generating audio files for your new voice pack.

```
> python3 generate_voice_pack.py --your_name '' --voice_name 'Murray'
```

You will need to provide at least the `--voice_name` parameter, but feel to investigate the other parameters with `python3 generate_voice_pack.py --help` or see an explanation elsewhere on this page. Note the requirement to include `--cpu_only` in the command line if not running with an nvidia GPU.

Logs will start to flow, showing the progress of the audio file generation. You can monitor the progress and any errors that occur, and stop the container at any time by pressing Ctrl+C in the terminal or with `docker stop crew-chief-autovoicepack` from another terminal window.

Optional: To run multiple of containers at once to greatly speed up the process, see the instructions elsewhere on this page.

Eventually, the script will create all ~10K audio files with the messages `All entries in audio_file_inventory.csv have been generated.` and `All radio check audio clips have been generated.`.

Once complete, you will now have a full voice pack in the `output` folder you mounted to your local machine. You can now add this voice pack to your CrewChief installation and enjoy a break from Jim!


### Common Task: Add your new voice pack to CrewChief
Presumably, you are running CrewChief on a Windows PC which you use for sim racing.

CrewChief voice audio files are stored in the CrewChiefV4 `sounds` folder, which is typically located at:
```
C:\Users\[user_name]\AppData\Local\CrewChiefV4\sounds\
```
It's possible you may have to allow viewing "hidden" files to see it. Also note that location can be overridden by the "Override default Sound Pack location" preference.

As an example, consider a voicepack with the root folder `Luis`.

1) Locate the voicepack files
- If your voicepack is already inside a .zip file, unzip it to a temporary location.
- Open two file explorer windows and navigate to both the CrewChief `...\sounds` folder and the folder containing the voicepack.
2) Within the `...\sounds` folder, create a new folder named `alt`.
3) Copy the `Luis` folder into the CrewChief `...\sounds\alt\` folder.
4) Radio check voices: Enter the `...sounds\alt\Luis` folder and you will see a subfolder named `radio_check_Luis`. Copy the `radio_check_Luis` folder into the CrewChief main `...\sounds\voice` folder. This folder has the official Jim voice as well as `radio_check_XXX` for each crew chief or spotter voice.
5) Done! Open CrewChief and you will see `Luis` as a choice in the right-side dropdown menu. The UI will restart to load the new voice pack, and you should hear Luis' voice perform a radio check along with your chosen spotter voice.


### Common Question: What other parameters can I use with the `generate_voice_pack.py` script?
| Parameter                | Description                                                                                                                                                                                                 |
|--------------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `--voice_name`            | Your custom name for this voice. Will be used as output folder name and appear in the CrewChief UI. Spaces will be removed, and probably avoid using UTF-8 and other characters.                        |
| `--voice_name_tts`        | The name of the voice as it should be pronounced by the TTS engine. For example, you may have a voice_name of 'Luis' but a voice_name_tts of 'Luees'. If not provided, the voice_name will be used.        |
| `--your_name`             | Your name, used by the Crew Chief to refer to you personally, baked into the generated audio. Defaults to empty text.                                                                                       |
| `--variation_count`       | Number of additional variations to generate for each audio file. Set to 0 to disable variations.                                                                                                           |
| `--output_audio_dir`      | Path to the folder where the generated audio files will be saved.                                                                                                                                       |
| `--disable_audio_effects` | Prevent applying audio effects to the generated audio files.                                                                                                                                               |
| `--disable_text_replacements` | Prevent applying text replacement rules to the generated audio files. Add or modify rules directly in generate_voice_pack.py.                                                                           |
| `--audio_inventory_file`  | Path to the CSV file containing the audio inventory.                                                                                                                                                        |
| `--original_inventory_order` | Do not randomize the order of the audio files in the inventory. Recommended to keep shuffling enabled when running multiple instances of the script in parallel.                                        |
| `--baseline_audio_dir`    | Path to the folder containing the baseline audio recordings which will be used to clone that speaker's voice.                                                                                           |
| `--skip_inventory`        | Skip generating audio files based on entries from the audio inventory file. Probably not what you want, but maybe useful during testing (for example, to skip directly to the radio check generation).      |
| `--skip_radio_check`      | Skip generating radio check audio clips.                                                                                                                                                                   |
| `--overwrite`             | Overwrite existing audio files.                                                                                                                                                                            |
| `--disable_deepspeed`     | Skip DeepSpeed during inference. Recommended to keep it enabled if possible as inference (TTS generation) is much faster, but it causes a longer startup time and noisy logs so may be helpful to disable during certain development steps. |
| `--voicepack_version`     | Version of the voice pack. This is used in the attribution file and elsewhere to identify newer or alternate versions. The default value is the current date.                                               |
| `--cpu_only`              | Run the process on the CPU instead of the GPU. This is much slower but is necessary if your PC does not have an CUDA-capable NVIDIA GPU. Implies --disable_deepspeed.                                      |



### Common Task: Restart a running crew-chief-autovoicepack container
crew-chief-autovoicepack has mostly [idempotent](https://en.wikipedia.org/wiki/Idempotence) behavior ("can be repeated or retried as often as necessary without causing unintended effects"), so you are free to start, stop, and restart the `docker run` or Docker Compose containers at any time.

1. Before generating each voice pack audio file, the generation script checks the output folder to see if that file already exists, and skips it if so (unless `--overwrite` is specified).

2. The order of the audio inventory file entries are randomly shuffled when each container starts (unless `--original_inventory_order` is specified). In practice, this breaks up the work into uniform chunks that can be run in parallel across multiple containers without needing any coordination beyond checking for file existence in the shared output folder.


### Common Question: How long does it take to generate a voice pack?
1 to 2 hours with a modern GPU, 4 to 12 hours with CPU only.

The overall duration depends on the number of phrases in the CrewChief audio inventory file (~10,000 by default), the container host machine's CPU/GPU/RAM, whether crew-chief-autovoicepack is running with a GPU or in CPU-only mode, the number of variants (the `--variant_count` parameter), and the number of containers running in parallel.

In general, a single `docker run` container in CPU-only mode will take several minutes to initialize, then should start generating audio files, with each generation taking a few seconds or less. The number of these steps can be estimated as the number of phrases in the audio inventory file times the number of variants.

A 24GB GPU (RTX 4090/3090) will enable running 8 replicas in parallel (see instructions on this page), each many times faster than the CPU version. 16GB GPUs (RTX 4080/4070/4060Ti) or lower will support proportionally fewer replicas before being constrained by GPU VRAM. Even with a 8GB GPU and a single container running the audio generation script, using a GPU will be much faster than the CPU-only mode.


### Common Question: Can I remove individual audio files from the output folder?
Yes! You are encouraged to review and curate the output files (if you have the time/interest) by removing any "bad" ones.

Any files removed from the voicepack output folder will be regenerated the next time the `generate_voice_pack.py` script is run, and all the existing files will be (very quickly) skipped.

This allows you to identify and simply delete any corrupt or poor-quality audio files, and quickly run the docker container (`docker run ...`) and generate script again on-demand until you get things perfect.

Note that CrewChief itself doesn't care how many files are in each folder, so there is no minimum or maximum. More files just mean more variety in the voice pack, as CrewChief will randomly play one of the files from the folder.

Additionally, this means you can reduce variety by deleting any files you want as long as there is at least one file left in the folder. If you want to remove a file (and its variants ending in '-1.wav', '-2.wav', etc.) permanently across multiple runs, edit the audio inventory file to remove the corresponding rows entirely.


### Common Question: How do I install a voice pack?
#TODO, mention how to find the CrewChiefV4 install folder, and where to unzip the voice pack files.


### Common Question: Everyone hates Docker... why is this packaged exclusively as a Docker image??
Docker has a long history of being painful to install, configure, update, etc ... but the benefits here are undeniable:

1) Enables CrewChief voice pack creation for the widest audience possible
2) A Docker image built today will continue to function the same even if run many years from now
3) It can be nightmarish even for technical users to identify and solve all the Python dependencies and OS packages needed to install and run advanced machine learning models reliably from their own machine.
4) No conda envs or virtualenvs to manage, No dependency hell or conflicting versions of tools and APIs
5) Easily supports all relevant hardware configurations (CPU-only, CUDA GPU, etc.) and operating systems
6) Packages multiple gigabytes of complex dependencies into a single file, easily downloadable with friendly tools like `docker pull` or the Docker Desktop GUI
7) Trivial to run multiple replicas in parallel to speed up computation (via Docker Compose)
8) Can be run on a cloud server just as easily as a local machine


### Uncommon Task: Local development without Docker
- clone the repo locally: `git clone ...`
- install all necessary OS packages and python dependencies as closely as possible to those specified in the Dockerfile
- if using a GPU:
  - ensure recent nvidia and CUDA drivers
  - install nvidia container toolkit (Linux): https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html
  - optionally install deepspeed (recommended)
- install coqui-tts, shown in the Dockerfile
- coqui should be operational from the command line:
  - `tts --model_name tts_models/multilingual/multi-dataset/xtts_v2 --speaker_idx 'Claribel Dervla' --language_idx en --use_cuda true --out_path /tmp/x.wav --text 'This is a test.'`
- modify `generate_voice_pack.py` as needed to point to the right resource locations 


### Common Task: Running multiple containers in parallel to speed up voice pack generation
To speed up the process of generating a voice pack, you can run multiple containers in parallel on the same machine. This is useful in both CPU-only and GPU modes.

Instead of starting a single instance of the Docker container with `docker run ...` you can use Docker Compose and the crew-chief-autovoicepack `docker-compose.yml` file to start, stop, and restart multiple containers at once.

1. Edit the `docker-compose.yml` file to specify the number of containers you want to run in parallel.
2. Ensure you have downloaded the crew-chief-autovoicepack Docker image with `docker pull crew-chief-autovoicepack:v0.1`. You can confirm this with `docker image list crew-chief-autovoicepack`.
3. Start the containers with `docker compose up -d crew-chief-autovoicepack`
4. Monitor the progress of the audio generation with `docker compose logs -f`
5. Stop the containers with `docker compose down`
6. Repeat as needed to generate all the audio files for your voice pack.

NOTE: Annoyingly, there is a difference between `docker-compose` (dash) and `docker compose` (space), based on legacy choices around installing Docker Compose as a plugin versus standalone. `docker compose` is the correct version, and hopefully works for you from the command line ("Command Prompt", "Terminal", etc. depending on your operating system). If you installed Docker Desktop for Windows or macOS, you should have `docker compose` available by default, and should not need to install anything additional.


### Uncommon tasks: Rebuilding the crew-chief-autovoicepack Docker image
Note that you can avoid rebuilding the container image simply by mounting the local version of the files you want to modify in place of the version baked into the container image, such as `generate_voice_pack.py` or `audio_file_inventory.csv`. See instructions elsewhere on this page for how to mount a local file into the container.

However, if you make signficant changes to the files in the repo, including the Dockerfile, you may prefer to rebuild the Docker image (`docker build ...`) to include those changes.

The process may seem daunting the first time, but it will complete very quickly each run after the initial build since Docker caches the intermediate steps. This means you won't have to wait to download the base Linux image, apt packages, pytorch dependencies, the machine learning models, etc. but you can change the python code and rebuild the image in seconds.

You may encounter dependency resolution issues or other software supply chain problems, but hopefully are able to work through them with the help of the community or the Internet.

From the crew-chief-autovoicepack root folder:
```
> DOCKER_BUILDKIT=1 docker build -f Dockerfile .
```
On Windows, it's easiest to run this from the WSL2 (Linux) bash prompt, but it may also work from the Windows Command Prompt or PowerShell.

If you are using Docker Desktop, you may also see the build process appear on the "Active Builds" tab of "Builds". You can review the progress or check error logs there.

Once the image has been rebuilt, you can run it with `docker run ...` as usual.


### Common Question: How do I know it's working/running/progressing?
After starting the container via `docker run ...` and from the shell prompt starting the `generate_voice_pack.py` script, you will see initialization messages for several minutes (especially if DeepSpeed is enabled), but eventually you should see a stream of messages indicating the progress of the audio file generation:

```
Generating audio for 80 - 'right 5' -> 'right 5'
File created at: ./output/Luis/voice/codriver/corner_5_right_reversed/117-a.wav
File created at: ./output/Luis/voice/codriver/corner_5_right_reversed/117-b.wav
File created at: ./output/Luis/voice/codriver/corner_5_right_reversed/117-c.wav
```

These messages will continue until the script has processed all the phrases in the audio inventory file. If you see no messages for a long time, it is safe to investigate, including stopping or restarting the container again later (see relevant question elsewhere on this page). In the example above, it's generating audio files for the 80th phrase in the audio inventory file, out of a total of almost 10,000 phrases.

When running multiple containers in parallel via `docker compose`, you can view the logs of all replica containers at once with `docker compose logs -f` (Ctrl+C to exit).

Based on how quickly these messages are flowing, you can estimate how long the total process will take.

Bonus -- Easy ways to gauge the voicepack quality in real-time:
- Manually: Browse the `output` folder, clicking through to each folder and listening to the audio files as they are generated
- Use an audio player that will let you listen to an entire folder tree
- (Linux) Loop over and play each file in the output folder: `find output/Luis/ -type f -name '*.wav' | while read -r file; do echo "$file"; paplay "$file"; done`


### Common Question: If I stop or delete the container, will I lose progress?
No, since you mounted a local folder into the container, all the generated audio files will be saved there and will persist even if the container is stopped or deleted. Restart where you left off, or clear the output folder and start fresh.


### Common Question: I made a change while the process was running, will it be picked up? What about the previously created audio files?
If you make a change to the `generate_voice_pack.py` script or the `audio_file_inventory.csv` file while the process is running, the changes will not be picked up until you stop and restart the container (and even in that case, you'll see changes if those individual files are directly mounted into the container as shown elsewhere here).


### Common Question: How much storage space is used by each voicepack?
A typical `crew-chief-autovoicepack` voicepack is 2GB or more.

The official CrewChief "Jim" audio files are ~0.5GB.

The .wav files generated by `crew-chief-autovoicepack` are (perhaps unnecessarily) larger since they are stored with 32-bit resolution at 24KHz. There are also many more .wav files in your new voicepack due to the `--variation_count` parameter, which defaults to 2, but can be set to 0 to disable variations and save storage space (or higher to potentially generate more varied audio at the cost of storage).


### Common Question: I have plenty of disk space, why shouldn't I set variation_count to 25 or more?
Feel free to experiment. I saw diminishing returns after 3-5 variants, as since the exact text stays the same, eventually successive attempts will often sound similar enough to one of the previous results that it's not worth the extra storage space.

If you want to add real variety, consider adding more rows to the audio inventory file, which is mentioned in detail elsewhere on this page.


### Common Question: How can I add my own phrases and commentary to the voice pack?
It's important to realize that CrewChief has a fixed understanding of which folders contain the various phrases it will pull from when the conditions arise.

So upon seeing a Yellow Flag in the sim, CrewChief will determine the details (for example, let's say it's a "full course yellow") and play a random selection from the .wav files in the `.../voice/flags/fc_yellow_in_progress_usa` folder.

This corresponds to these rows of the `audio_file_inventory.csv` file:

| audio_filename                               | original_text                            |
|----------------------------------------------|------------------------------------------|
| \voice\flags\fc_yellow_in_progress_usa:1.wav | we're under caution, the pace car is out |
| \voice\flags\fc_yellow_in_progress_usa:2.wav | full course yellow, pace car is out      |
| \voice\flags\fc_yellow_in_progress_usa:3.wav | full course yellow, we're under caution  |
| \voice\flags\fc_yellow_in_progress_usa:4.wav | full course yellow, pace car is out      |
| \voice\flags\fc_yellow_in_progress_usa:5.wav | we're under caution, full course yellow  |
| \voice\flags\fc_yellow_in_progress_usa:6.wav | full course yellow, pace car is out      |
| \voice\flags\fc_yellow_in_progress_usa:7.wav | we're under caution, full course yellow  |

Understanding this, **you can add your own phrases** to the voice pack by editing the `audio_file_inventory.csv` file based on the existing CrewChief "intents" represented by the folder names in the `audio_filename` column.

For example, if you want to add a new phrase which is played when CrewChief looks for audio intended for `didn't understand`, add a new row to `audio_file_inventory.csv` file like this:

| audio_filename                               | original_text                      |
|----------------------------------------------|------------------------------------|
| \voice\acknowledge\didnt_understand:15.wav   | I have no idea what you're saying! |

...and now alongside the existing 14 official phrases that will be generated and output to the `../didnt_understand` folder, `crew-chief-autovoicepack` will generate a new totally custom "I have no idea what you're saying!" audio clip.

If you don't want some or all of the original phrases, simply remove them. You can even remove (or fail to generate) an entire folder and Crew Chief will just do nothing when triggered with that intent.

Important: You cannot create an entirely new custom phrase (like "That last incident is under investigation") unless it corresponds to an "intention" (folder name in the audio inventory) that CrewChief already recognizes, but you can add an unlimited number and variety of new phrases to any of the existing folders.

Additionally, there is nothing stopping you from cleverly co-opting a certain folder for your own purposes, but the audio will still be only play when CrewChief is triggered by the scenario hinted at by the folder name. i.e. We aren't changing any CrewChief logic, just adding some extra .wav files for it to play in the standard situations.

Recommended places to start:
- Add a bunch of custom celebratory messages to `\voice\lap_counter\finished_race_good_finish`
- Berate your terrible performance with new rows for `\voice\lap_counter\finished_race_last`
- In general, start with the same value for the `text_for_tts` column the same as `original_text`
- Perfect the bad pronounciation of your favorite corners in `\voice\corners` by adding a different value for the `text_for_tts` column.


### Common Question: My generated voice pack sounds a lot worse and has a lot more corrupted audio files than the official repo's voice packs. What will improve my results?
The source of your issues is very likely from imperfections in the input audio recordings. You must be ruthless in trimming out silence, and the files must be saved in exactly the right format for the coqui xtts model to work effectively.

- Key considerations:
  1) 10 seconds or less per clip (longer is ignored)
  2) 25 or fewer clips (10 is fine)
  3) WAV file format details: 32-bit float PCM, 22.5 kHz sample rate, mono channel
  4) Recordings MUST be high-quality, with no background noise, clipping, or distortion
  5) Recordings must be normalized to the full dynamic range
  6) Recordings must be ruthlessly trimmed to remove all silence at the beginning or end of every file
  7) For any other silence or pauses longer than ~1 second, split the clip into two separate clips at that point and trim the silence away from the start and end
  8) Simply delete any adversarial or low-quality clips, usually easier than trying to fix them
  9) Don't obsess over capturing the voice in a wide emotional range, as the xtts model tends to diminish those aspects anyway. Similarly, be deliberate, but don't worry too much about capturing a specific phonetic range -- it's hard to figure out which details will make it into the cloned voice without experimenting.

- Use a modern audio file editor (ocenaudio, Audacity, etc.) to view the waveform for each audio clip.
- Look at the provided voice recordings in the repo's `output/baseline` folder for examples of what recorded voice clips should look like.
- The `record_elevenlabs_voice.py` script automatically captures an appropriate number of suitable-length high-quality voice samples, applying suitable audio effects such as normalization, and saving them in the correct format.
- Audio from YouTube videos (for example, captured from an interview with a tool like [yt-dlp](https://github.com/yt-dlp/yt-dlp)) is generally usable after applying ALL the considerations above, but the speaker's voice needs to be 100% isolated with no background noise, music, chatter, etc.
- Recording your own voice all works well, following the guidelines above.


### Common Question: How do I report a bug?
Feel free to use the "Issues" tab at the very top of the repo homepage to report any bugs, issues, or feature requests you have. Please include as much detail as possible, including the command you ran, the output you saw, and any relevant context about your system (OS, hardware, etc.).


### Common Question: How do I contribute to the project?
Feel free to fork the repo, make your changes, and submit a pull request. Please include a detailed description of the changes you made, why you made them, and any relevant context about your system (OS, hardware, etc.). If you have any questions, feel free to ask in the "Issues" tab at the very top of the repo homepage.

### Common Question: How do I create a voice pack in a different language?
I've not done this since I only use English, but here's a rough outline of suggested steps:

- Machine-translate the `original_text` column of `audio_file_inventory.csv` using an LLM like ChatGPT. This can be done iteratively, copy/pasting an acceptable number of rows at a time to the LLM, or fully automated via API calls.
- After translation, manually review the csv file in a tool like Excel or LibreOffice Calc
- Manually edit any translations that are incorrect
- Optionally, tweak the TTS pronounciation column for troublesome entries
- Generate the voicepack using the normal process
  - Important: ensure that your updated `audio_file_inventory.csv` file is mounted into the container using the `docker run ... -v ...` command line parameter.
  - For example, use `docker run ... -v /path/to/MY_CUSTOM_AUDIO_FILE_INVENTORY.csv:/app/audio_file_inventory.csv ...` to override the default phrases with your translated phrases.
- Let the voicepack generate for a few minutes
- Review the output audio files to judge how well it worked

The coqui xtts model is multilingual and should work well with many languages, but the quality of the translations will depend on the quality of the machine translation and the quality of the original audio recordings. You may need to experiment with different translation techniques to get the best results, but crew-chief-autovoicepack will do most of the work for you -- imagine having to record and edit ten-thousand audio clips yourself (you'd need the patience of a Belowski).


### Uncommon Question: My voice pack works, but I don't hear the radio check at startup?
CrewChief has a common folder for all radio check audio clips, generally the main `.../sounds/voice/` folder. You will see other radio check folders like `radio_check_Jim`, `radio_check_Mike`, etc. in this folder. If you do not see a folder with the name of your voicepack (like `radio_check_Luis`), it's possible the `radio_check_Luis` folder was not copied into this main folder from the root voicepack folder. This has to be done manually, as noted in the voice pack installation step.


### Uncommon Tasks: Recommended developer workflow
- Clone repo locally
- Edit the audio inventory file and/or generate_voice_pack.py as needed
- Rebuild the docker image (see recommended docker commands elsewhere on this page)
- Run the docker image with the output folder mounted to a local folder
- From the container's bash prompt, use the up arrow and select a relevant command line to start with
_ Edit, rebuild, run, over and over while reviewing the output/ dir results


### References
- CrewChief: https://gitlab.com/mr_belowski/CrewChiefV4
- CrewChief forum thread on adding new voice packs: https://thecrewchief.org/showthread.php?825-Authoring-alternative-Crew-Chief-voice-packs

