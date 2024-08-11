

### How to mount a custom audio inventory file
docker run -v /path/to/local/file:/path/in/container/file <image_name>

### Capabilities
- automatically generate a full CrewChief voicepack from 30 seconds of any voice
- supports all CrewChief phrases and sims (Assetto Corsa, ACC, iRacing, etc.)
- natural-sounding speech using free software
- no-cost, unlimited usage, runs locally on your PC
- easily replace original CrewChief commentary with fully custom phrases
- use ANY voice you want: your own, a friend's, a celebrity's, etc.
- use any professional-quality voice from ElevenLabs.io as your CrewChief (for free)
- possible to generate voice packs in any language (requires machine/human text translation)
- fast -- 1-2 hours for tens of thousands of audio files (RTX 3090)
- runs on any hardware, Windows/Mac/Linux, CPU-only or CUDA GPU
- elegantly packaged as a ready-to-use Docker image
- friendly Python code you are encouraged to tweak
- remove (or introduce!) swear words and regional language quirks

### Download new voicepacks created by crew-chief-autovoicepack
As a shortcut, use one of these full, high-quality replacement voices for CrewChief. Unzip as mentioned [below](#installing_a_voicepack).
- Sally
- Don
- Blake
- Rajan
- Shannon
- Jamal
- David
- Norm
- Brad
- Paul
- Hiroshi
- Ana
- Luis
- Madeline

### Known Issues
- generated voices do not exactly match the original speaker's voice
- poor or incorrect TTS pronounciations (driver names, corner names, etc.)
- occasional garbled or corrupt audio (a few percent of the total)
- rarely, may fail applying audio effects and leave the interim x.raw.wav file and no x.wav file
- may adopt incorrect accent or diminish input accent on certain TTS phrases
- emotional inflection is worse than a human voice actor
- speed/pace is not easily adjustable (i.e. "rushed" CrewChief phrases are not accomodated)
- voicepack name must use ASCII characters (e.g. UTF-8 chars like é, ñ, are not supported) 

### Translating to other languages
- probably want to machine-translate the audio inventory file
- then review and hand edit any translations that are incorrect
- after testing, probably need to tweak the TTS pronounciation column

### Recommended developer workflow
- Clone repo locally
- Edit the audio inventory file and/or generate_voice_pack.py as needed
- Rebuild the docker image (see recommended docker commands elsewhere on this page)
- Run the docker image with the output directory mounted to a local directory
- From the container's bash prompt, use the up arrow and select a relevant command line to start with
_ Edit, rebuild, run, over and over while reviewing the output/ dir results

### References
- CrewChief: https://gitlab.com/mr_belowski/CrewChiefV4
- CrewChief official thread on adding new voice packs: https://thecrewchief.org/showthread.php?825-Authoring-alternative-Crew-Chief-voice-packs

### Possible Future Improvements
- Incorporate RVC (Real Voice Cloning) to better match the original speaker's voice -- this would take the TTS generated audio and post-process it to sound even more like the original. Could also be applied to the original CrewChief "Jim" voice pack audio to retain the emotional inflection and pacing (though unavoidably inheriting the regional jargon and matey-ness).


### Common task: Start crew-chief-autovoicepack container without using a GPU (CPU-only mode)
Launch the container with Docker, leaving off the `--gpus all` parameter, and making sure to mount the `output` directory to a local directory.

Example (Linux):
`docker run --rm -it --name crew-chief-autovoicepack -v /tmp/crew-chief-autovoicepack/output:/app/output crew-chief-autovoicepack:v0.1`

After starting the container, you should see an indication the CUDA drivers were not able to detect a compatible NVIDIA GPU, which is expected in this case:
```
WARNING: The NVIDIA Driver was not detected.  GPU functionality will not be available.
   Use the NVIDIA Container Toolkit to start this container with GPU support.
```

From the container's bash prompt, you can run the `generate_voice_pack.py` script as needed.  Note the requirement to include `--cpu_only` in the command line when running the script in CPU-only mode.

For example:
`python3 generate_voice_pack.py -i /app/input/crewchief_audio_inventory.csv --voice_name "MyCrewChief" --cpu_only`

To run multiple of these containers at once to greatly speed up the process, see the instructions elsewhere on this page.


### Common Task: Restart a running crew-chief-autovoicepack container
crew-chief-autovoicepack has mostly [idempotent](https://en.wikipedia.org/wiki/Idempotence) behavior ("can be repeated or retried as often as necessary without causing unintended effects"), so you are free to start, stop, and restart the `docker run` or Docker Compose containers at any time.

1. Before generating each voice pack audio file, the generation script checks the output directory to see if that file already exists, and skips it if so (unless `--overwrite` is specified).

2. The order of the audio inventory file entries are randomly shuffled when each container starts (unless `--original_inventory_order` is specified). In practice, this breaks up the work into uniform chunks that can be run in parallel across multiple containers without needing any coordination beyond checking for file existence in the shared output directory.


### Common Question: How long does it take to generate a voice pack?
1 to 2 hours with a modern GPU, 4 to 12 hours with CPU only.

The overall duration depends on the number of phrases in the CrewChief audio inventory file (~10,000 by default), the container host machine's CPU/GPU/RAM, whether crew-chief-autovoicepack is running with a GPU or in CPU-only mode, the number of variants (the `--variant_count` parameter), and the number of containers running in parallel.

In general, a single `docker run` container in CPU-only mode will take several minutes to initialize, then should start generating audio files, with each generation taking a few seconds or less. The number of these steps can be estimated as the number of phrases in the audio inventory file times the number of variants.

A 24GB GPU (RTX 4090/3090) will enable running 8 replicas in parallel (see instructions on this page), each many times faster than the CPU version. 16GB GPUs (RTX 4080/4070/4060Ti) or lower will support proportionally fewer replicas before being constrained by GPU VRAM. Even with a 8GB GPU and a single container running the audio generation script, using a GPU will be much faster than the CPU-only mode.


### Common Question: Can I remove individual audio files from the output directory?
Yes! You are encouraged to review and curate the output files (if you have the time/interest) by removing any "bad" ones.

Any files removed from the voicepack output directory will be regenerated the next time the `generate_voice_pack.py` script is run, and all the existing files will be (very quickly) skipped.

This allows you to identify and simply delete any corrupt or poor-quality audio files, and quickly run the docker container (`docker run ...`) and generate script again on-demand until you get things perfect.

Note that CrewChief itself doesn't care how many files are in each directory, so there is no minimum or maximum. More files just mean more variety in the voice pack, as CrewChief will randomly play one of the files from the directory.

Additionally, this means you can reduce variety by deleting any files you want as long as there is at least one file left in the directory. If you want to remove a file (and its variants ending in '-1.wav', '-2.wav', etc.) permanently across multiple runs, edit the audio inventory file to remove the corresponding rows entirely.


### Common Question: How do I install a voice pack?
#TODO, mention how to find the CrewChiefV4 install directory, and where to unzip the voice pack files.


### Common Question: Everyone hates Docker... why did you package this exclusively as a Docker image?
Docker has a long history of being painful to install, configure, update, etc ... but the benefits here are undeniable:

1) Enables CrewChief voice pack creation for the widest audience possible
2) It can be nightmarish even for highly-technical users to identify and solve all the Python dependencies and OS packages needed to install and run the text-to-speech tools reliably from their own machine.
3) No conda envs or virtualenvs to manage, No dependency hell or conflicting versions of tools and APIs
5) A Docker image built today will continue to function the same even if run many years from now
6) Easily supports all relevant hardware configurations (CPU-only, CUDA GPU, etc.) and operating systems
7) Can be run on a cloud server just as easily as a local machine
8) Is easily distributed as one single file, downloadable with friendly tools like `docker pull` or the Docker Desktop GUI


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


### Common tasks: Rebuilding a Docker image
When you make changes to the Python code in `generate_voice_pack.py` or the Dockerfile, you will need to rebuild the Docker image (`docker build ...`) to include those changes so when the container (based on this image) runs with `docker run ...` it has the changes you made.

The process may seem daunting the first time, but it will complete very quickly each run after the initial build since Docker caches the intermediate steps. This means you won't have to wait to download the base Linux image, apt packages, pytorch dependencies, the machine learning models, etc. but you can change the python code and rebuild the image in seconds.

From the crew-chief-autovoicepack root directory:
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


### Common Question: How do I stop the container and exit the shell prompt?
TBD

### Common Question: I made a change while the process was running, will it be picked up? What about the previously created files?
TBD

### Common Question: How much disk space will this take?

### Common Question: How much input audio do I need to provide? Is more better?
TBD

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
- Look at the provided voice recordings in the repo's `output/baseline` directory for examples of what recorded voice clips should look like.
- The `record_elevenlabs_voice.py` script automatically captures an appropriate number of suitable-length high-quality voice samples, applying suitable audio effects such as normalization, and saving them in the correct format.
- Audio from YouTube videos (for example, captured from an interview with a tool like [yt-dlp](https://github.com/yt-dlp/yt-dlp)) is generally usable after applying ALL the considerations above, but the speaker's voice needs to be 100% isolated with no background noise, music, chatter, etc.
- Recording your own voice all works well, following the guidelines above.


### Common Question: How do I report a bug?
Feel free to use the "Issues" tab at the very top of the repo homepage to report any bugs, issues, or feature requests you have. Please include as much detail as possible, including the command you ran, the output you saw, and any relevant context about your system (OS, hardware, etc.).


### Common Question: How do I contribute to the project?
Feel free to fork the repo, make your changes, and submit a pull request. Please include a detailed description of the changes you made, why you made them, and any relevant context about your system (OS, hardware, etc.). If you have any questions, feel free to ask in the "Issues" tab at the very top of the repo homepage.

