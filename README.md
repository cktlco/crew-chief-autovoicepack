# crew-chief-autovoicepack
## Automatically generate a full CrewChief voice pack from any 30-second recording.


## 🧠️ Capabilities
- **natural-sounding** AI generated speech
- supports **all CrewChief phrases** and sims (Assetto Corsa, ACC, iRacing, etc.)
- **no-cost**, unlimited usage, run locally on your PC
- easily replace original CrewChief commentary with **fully custom phrases**
- **use ANY voice**: your own, a friend, or celebrity
- easily import high-quality professional **voices from ElevenLabs.io** (for free)
- multiply the original phrase library with automatic **variations**
- generate voice packs **in any language** (requires machine/human text translation)
- **fast**: 1-2 hours to create **30,000 audio files** (RTX 3090)
- runs on **any hardware**, Windows/Mac/Linux, CPU-only or Nvidia GPU
- elegantly packaged as a **ready-to-use** Docker image
- **friendly** Python code you are encouraged to tweak
- remove (or introduce!) swear words, gender assumptions, and regional language quirks


[//]: # (## 🎥 Video demonstration)
[//]: # (TBD)


## ⏬ In a hurry? Download an existing voice pack
Make your own, or download one of these ready-to-go **full replacement voices for CrewChief**.

[Unzip](#-common-task-add-your-new-voice-pack-to-crewchief) and use immediately. Over 30,000 .wav files in each pack.

|                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      |                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      |                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          |
|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| <img alt="Portrait of Sally" src="resources/images/Sally.webp" width="256px"><br/>**Sally**<br/><audio controls=""><source src="resources/audio/Sally_speech_demo.wav" type="audio/wav"></audio>       <br/>[[download 1.7GB]](https://github.com/cktlco/crew-chief-autovoicepack/releases/download/v1.0.0/crew-chief-autovoicepack-Sally-1of1.zip)                                                                                                                                                  | <img alt="Portrait of Don" src="resources/images/Don.webp" width="256px"><br/>**Don**<br/><audio controls=""><source src="resources/audio/Don_speech_demo.wav" type="audio/wav"></audio><br/>[[download 1.6GB]](https://github.com/cktlco/crew-chief-autovoicepack/releases/download/v1.0.0/crew-chief-autovoicepack-Don-1of1.zip)                                                                                                                                                                   | <img alt="Portrait of Norm" src="resources/images/Norm.webp" width="256px"><br/>**Norm**<br/><audio controls=""><source src="resources/audio/Norm_speech_demo.wav" type="audio/wav"></audio><br/>[[download 1.6GB]](https://github.com/cktlco/crew-chief-autovoicepack/releases/download/v1.0.0/crew-chief-autovoicepack-Norm-1of1.zip)                                                                                                                                                  |
| <img alt="Portrait of Shannon" src="resources/images/Shannon.webp" width="256px"><br/>**Shannon**<br/><audio controls=""><source src="resources/audio/Shannon_speech_demo.wav" type="audio/wav"></audio><br/>[[part 1 - 1.8GB]](https://github.com/cktlco/crew-chief-autovoicepack/releases/download/v1.0.0/crew-chief-autovoicepack-Shannon-1of2.zip)<br/>[[part 2 - 0.1GB]](https://github.com/cktlco/crew-chief-autovoicepack/releases/download/v1.0.0/crew-chief-autovoicepack-Shannon-2of2.zip) | <img alt="Portrait of Rajan" src="resources/images/Rajan.webp" width="256px"><br/>**Rajan**<br/><audio controls=""><source src="resources/audio/Rajan_speech_demo.wav" type="audio/wav"></audio><br/>[[download - 1.6GB]](https://github.com/cktlco/crew-chief-autovoicepack/releases/download/v1.0.0/crew-chief-autovoicepack-Rajan-1of1.zip)<br/><br/>                                                                                                                                             | <img alt="Portrait of Jamal" src="resources/images/Jamal.webp" width="256px"><br/>**Jamal**<br/><audio controls=""><source src="resources/audio/Jamal_speech_demo.wav" type="audio/wav"></audio><br/>[[download - 1.7GB]](https://github.com/cktlco/crew-chief-autovoicepack/releases/download/v1.0.0/crew-chief-autovoicepack-Jamal-1of1.zip)<br/><br/>                                                                                                                                 |
| <img alt="Portrait of David" src="resources/images/David.webp" width="256px"><br/> **David**<br/><audio controls=""><source src="resources/audio/David_speech_demo.wav" type="audio/wav"></audio><br/>[[download - 1.7GB]](https://github.com/cktlco/crew-chief-autovoicepack/releases/download/v1.0.0/crew-chief-autovoicepack-David-1of1.zip)<br/><br/>                                                                                                                                            | <img alt="Portrait of Ana" src="resources/images/Ana.webp" width="256px"><br/>**Ana**<br/><audio controls=""><source src="resources/audio/Ana_speech_demo.wav" type="audio/wav"></audio><br/>[[part 1 - 1.8GB]](https://github.com/cktlco/crew-chief-autovoicepack/releases/download/v1.0.0/crew-chief-autovoicepack-Ana-1of2.zip)<br/>[[part 2 - 0.1GB]](https://github.com/cktlco/crew-chief-autovoicepack/releases/download/v1.0.0/crew-chief-autovoicepack-Ana-2of2.zip)                         | <img alt="Portrait of Blake" src="resources/images/Blake.webp" width="256px"><br/>**Blake**<br/><audio controls=""><source src="resources/audio/Blake_speech_demo.wav" type="audio/wav"></audio><br/>[[part 1 - 1.8GB]](https://github.com/cktlco/crew-chief-autovoicepack/releases/download/v1.0.0/crew-chief-autovoicepack-Blake-1of2.zip)<br/>[[part 2 - 0.2GB]](https://github.com/cktlco/crew-chief-autovoicepack/releases/download/v1.0.0/crew-chief-autovoicepack-Blake-2of2.zip) |
| <img alt="Portrait of Paul" src="resources/images/Paul.webp" width="256px"><br/>**Paul**<br/><audio controls=""><source src="resources/audio/Paul_speech_demo.wav" type="audio/wav"></audio><br/>[[part 1 - 1.8GB]](https://github.com/cktlco/crew-chief-autovoicepack/releases/download/v1.0.0/crew-chief-autovoicepack-Paul-1of2.zip)<br/>[[part 2 - 0.1GB]](https://github.com/cktlco/crew-chief-autovoicepack/releases/download/v1.0.0/crew-chief-autovoicepack-Paul-2of2.zip)                   | <img alt="Portrait of Hiroshi" src="resources/images/Hiroshi.webp" width="256px"><br/>**Hiroshi**<br/><audio controls=""><source src="resources/audio/Hiroshi_speech_demo.wav" type="audio/wav"></audio><br/>[[part 1 - 1.8GB]](https://github.com/cktlco/crew-chief-autovoicepack/releases/download/v1.0.0/crew-chief-autovoicepack-Hiroshi-1of2.zip)<br/>[[part 2 - 0.9GB]](https://github.com/cktlco/crew-chief-autovoicepack/releases/download/v1.0.0/crew-chief-autovoicepack-Hiroshi-2of2.zip) | <img alt="Portrait of Bart" src="resources/images/Bart.webp" width="256px"><br/>**Bart**<br/><audio controls=""><source src="resources/audio/Bart_speech_demo.wav" type="audio/wav"></audio><br/>[[download - 1.5GB]](https://github.com/cktlco/crew-chief-autovoicepack/releases/download/v1.0.0/crew-chief-autovoicepack-Bart-1of1.zip)<br/><br/>                                                                                                                                      |
| <img alt="Portrait of Luis" src="resources/images/Luis.webp" width="256px"><br/>**Luis**<br/><audio controls=""><source src="resources/audio/Luis_speech_demo.wav" type="audio/wav"></audio><br/>[[download - 1.6GB]](https://github.com/cktlco/crew-chief-autovoicepack/releases/download/v1.0.0/crew-chief-autovoicepack-Luis-1of1.zip)                                                                                                                                                            | <img alt="Portrait of Madeline" src="resources/images/Madeline.webp" width="256px"><br/>**Madeline**<br/><audio controls=""><source src="resources/audio/Madeline_speech_demo.wav" type="audio/wav"></audio><br/>[[download - 1.5GB]](https://github.com/cktlco/crew-chief-autovoicepack/releases/download/v1.0.0/crew-chief-autovoicepack-Madeline-1of1.zip)                                                                                                                                        |                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          |


## 🚀 Quickstart
1. **Prepare 30 seconds of audio** -- record your own voice or use ElevenLabs
2. Run `generate_voice_pack.py` from a **Docker container** ([full instructions](#-common-task-generate-a-full-crewchief-voice-pack)).
3. **Add the new voice pack** to CrewChief ([full instructions](#-common-task-add-your-new-voice-pack-to-crewchief)).


## 🚧️ Known Issues
- occasional **poor or incorrect TTS pronunciations** (driver names, corner names, etc.)
- occasional **garbled or corrupt audio** (a few percent of the total)
- generated voices **do not exactly match the original** speaker's voice
- **speed/pace** is not easily adjustable (i.e. "rushed" CrewChief phrases are not rushed)
- minor: may adopt incorrect accent or diminish original accent on certain phrases
- minor: emotional inflection is worse than a human voice actor
- minor: voice pack name must use ASCII characters (e.g. UTF-8 chars like é, ñ, are not supported)


## 🎙️Common Task: Bootstrap your voice pack with an Elevenlabs.io voice 
[Elevenlabs.io](https://elevenlabs.io/) provides a professional-quality text-to-speech service that can be used to **generate high-quality baseline recordings** for use with `crew-chief-autovoicepack`. This is a great way to create a voice pack that sounds similar to a professional voice actor you choose.

1. **Sign up** for a free account at [Elevenlabs.io](https://elevenlabs.io/). Note your API key.
2. Browse the library and **select the voice you want to use** as the baseline for your voice pack
3. Find the "**voice id**" for the voice, from the Elevenlabs.io "voices" page
4. Use the provided `record_elevenlabs_voice.py` script to **create the baseline audio files**:
```
# from the running container
> python3 record_elevenlabs_voice.py --eleven_labs_api_key XXXXXXX --voice_id XXXXXXX --voice_name Luis
```
5. The script will generate a folder of **~20 "baseline" speech audio files based on this voice** in the `baseline` folder, including automatically normalizing and trimming silence.
```
> python3 generate_voice_pack.py --voice_name 'Luis' ...
```
6. You are **now ready to generate a full voice pack** using this voice as the baseline.


## 🎤 Common Task: Prepare recordings of your favorite voice
As an alternative to using an Elevenlabs.io voice, **record yourself or use an existing source like a YouTube video** (via a tool like [yt-dlp](https://github.com/yt-dlp/yt-dlp)).

1. Record at least **3x 10-second .wav file clips of the voice** for the baseline audio recordings (hint: record yourself speaking the `text_samples` in `record_elevenlabs_voice.py` for easy results). Only the first 10 seconds of each clip will be considered.
2. Trim the recordings to **remove all silence** at the beginning or end of every file, and remove silence longer than ~0.4 seconds from the middle of any file.
3. When saving, **format the audio files** as 32-bit float PCM WAV files with a 22.5 kHz sample rate and mono channel.
4. See the ["Common Task: My generated voice pack sounds a lot worse..."](#common-question-my-generated-voice-pack-sounds-a-lot-worse-and-has-a-lot-more-corrupted-audio-files-than-the-official-repos-voice-packs-what-will-improve-my-results) section **for more recommendations** on capturing audio.


## 📦 Common Task: Generate a full CrewChief voice pack
_Pre-requisite: At least 3x 10-second audio clips of your chosen voice._

This is an **automated process**. The only required software on your machine is **a working installation of Docker**.

The core concept is to **launch a temporary "Docker container"** which is a lightweight, isolated Linux virtual machine **that runs the crew-chief-autovoicepack processes**. You'll enable the container to access your GPU (optional), phrase inventory, and your baseline audio recordings. A Python **script running in the container will generate the audio files for your new voice pack**, which will be saved to the output folder on your local machine.

Using the Docker container enables you to **run a very sophisticated software environment on your own machine without having to manually install and manage** the dozens of required Python libraries, OS packages, and other dependencies yourself.

Windows or Mac users can **install Docker** via [Docker Desktop](https://docs.docker.com/desktop/), while Linux users can install via OS package manager or the official installation instructions.


### STEP 1. Install Docker
**Windows/Mac**: https://docs.docker.com/desktop/install/

On Windows, **Docker Desktop also requires WSL2** (Windows Subsystem for Linux) to be installed and enabled, which is straight-forward and covered in the Docker instructions. WSL2 and Docker Desktop also enable GPU access to your Docker containers.


**Linux**: https://docs.docker.com/engine/install/
 ... and enable Linux support for GPU containers: https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html

Note that all instructions here will be performed via the command line (not via the Docker Desktop GUI), so **ensure the basic Docker [hello-world](https://hub.docker.com/_/hello-world) tests work from a fresh terminal window** before proceeding:
```
C:\Users\YOUR_NAME> docker run hello-world

...
Pulling from library/hello-world
c1ec31eb5944: Pull complete ...

Hello from Docker!
This message shows that your installation appears to be working correctly.
```


### STEP 2. Download the crew-chief-autovoicepack Docker image with:
```
docker pull ghcr.io/cktlco/crew-chief-autovoicepack:v1.0.0
```
**This is a large file (21GB)** and will take time to download.

You can **confirm this step worked** with `docker image list crew-chief-autovoicepack`.


### STEP 3. Start a container to run the downloaded image

Windows:
```
docker run -it --rm --gpus all --name crew-chief-autovoicepack -v C:\Users\myuser\Desktop\crew-chief-autovoicepack\output:/app/output crew-chief-autovoicepack:v0.1`
```

Linux:
```
docker run -it --rm --gpus all --name crew-chief-autovoicepack -v ~/crew-chief-autovoicepack/output:/app/output crew-chief-autovoicepack:v0.1`
```

Important:
- Change the first part of the mounted folder path above (`-v ...`) to **a location on your local machine** where you want the generated audio files to be saved. Don't change the part after the colon (`:/app/output`).
- Remember to include the `--gpus all` parameter **if you have a modern NVIDIA GPU** and want to use it for the voice pack generation.

Running `docker run -it ...` will create a new container and drop you at a (customized) bash prompt:
```
crew-chief-autovoicepack > 
```

### STEP 4. Generate the audio files

From there, run the `generate_voice_pack.py` script to **start generating audio files** for your new voice pack.

```
> python3 generate_voice_pack.py --your_name 'Champ' --voice_name 'Luis'
```

You will need to **provide at least the `--voice_name` parameter**, but feel to investigate the other options with `python3 generate_voice_pack.py --help` or see an explanation elsewhere on this page.

The `voice_name` you provide will be **used to load the baseline audio recordings from the voice you are cloning** (from the `baseline\<voice_name>` folder), and will save the generated audio files in the `output` folder you mounted into the container. You populated the `baseline` folder **in a previous step**.

Note the requirement to include `--cpu_only` on the command line **when not running with an nvidia GPU**.

Within a few minutes, **logs will start to flow showing the progress** of the audio file generation. You can monitor the progress and any errors that occur, and stop the container at any time by pressing Ctrl+C in the terminal or with `docker stop crew-chief-autovoicepack` from another terminal window.

Optional: To run multiple of containers at once to **greatly speed up the process**, see [these instructions](#common-task-running-multiple-containers-in-parallel-to-speed-up-voice-pack-generation).

**Eventually, the script will complete** generation of all ~30K+ audio files with the messages `All entries in phrase_inventory.csv have been generated.` and `All radio check audio clips have been generated.`.

**You now have a full voice pack** in the `output` folder you mounted from your local machine. [Add this voice pack to your CrewChief installation](#common-task-add-your-new-voice-pack-to-crewchief) and enjoy a break from Jim!


## 🎯 Common Task: Add your new voice pack to CrewChief
Presumably, you are running CrewChief on a Windows PC which you use for sim racing.

**CrewChief voice audio files are stored in the CrewChiefV4 `sounds` folder**, which is typically located at:
```
C:\Users\[user_name]\AppData\Local\CrewChiefV4\sounds\
```

You can easily **open this folder directly** from the CrewChief UI via `File -> Open voice files folder`.

As an example, consider a voice pack with the root folder `Luis`.

1) **Locate** the voice pack files
- If your voice pack is already inside a .zip file, unzip it to a temporary location.
- Open two file explorer windows and navigate to both the CrewChief `...\sounds` folder (noted above) and the folder containing the voice pack.
2) Within the `...\sounds` folder, **create a new folder named `alt`** (if not already there)
3) **Copy** the entire `Luis` folder into the CrewChief `...\sounds\alt\` folder.
4) **Radio check voices**: Enter the `...\sounds\alt\Luis` folder and you will see a subfolder named `radio_check_Luis`. **Copy the `radio_check_Luis` folder into the CrewChief main `...\sounds\voice` folder.** This folder has the official Jim voice as well as `radio_check_XXX` for each crew chief or spotter voice.
5) **Done!** Open CrewChief and you will see `Luis` as a choice in the right-side dropdown menu. The UI will restart to load the new voice pack, and you should hear Luis' voice perform a radio check along with your chosen spotter voice.


## 🔧 Common Question: Which options can I use with the `generate_voice_pack.py` script?
| Option Name                   | Description                                                                                                                                                                    |
|-------------------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `--voice_name`                | **Your custom name for this voice.** Will be used as output directory name and appear in the CrewChief UI. Spaces will be removed. Avoid using UTF-8 and other special characters. |
| `--voice_name_tts`            | The name of the voice as it should be pronounced by the TTS engine. If not provided, the `voice_name` will be used.                                                            |
| `--your_name`                 | **Your name**, used by the Crew Chief to refer to you personally, baked into the generated audio.                                                                                  |
| `--variation_count`           | Number of **additional variations to generate** for each audio file. Set to 0 to disable variations.                                                                               |
| `--cpu_only`                  | Run the process using the **CPU only**, ignoring any available GPUs. Implies `--disable_deepspeed`.                                                                                |
| `--output_audio_dir`          | Path to the directory **where the generated audio files will be saved**.                                                                                                           |
| `--original_inventory_order`  | **Do not randomize the order** of the audio files in the inventory. Recommended to keep shuffling enabled when running multiple instances in parallel.                             |
| `--phrase_inventory`          | Path to the CSV file containing **the list of audio files to create** alongside the text used to generate them.                                                                    |
| `--baseline_audio_dir`        | Path to the directory containing the **baseline audio recordings** to clone the speaker's voice.                                                                                   |
| `--overwrite`                 | **Overwrite existing audio files**. If running multiple instances in parallel, all replicas will perform the work.                                                                 |
| `--disable_audio_effects`     | **Prevent applying audio effects** to the generated audio files.                                                                                                                   |
| `--disable_text_replacements` | **Prevent applying text replacement** rules to the generated audio files.                                                                                                          |
| `--disable_deepspeed`         | **Skip DeepSpeed** during inference. Useful to disable during certain development steps.                                                                                           |
| `--voicepack_version`         | **Version of the voice pack**, used in the attribution file and elsewhere to identify newer or alternate versions.                                                                 |
| `--skip_inventory`            | **Skip generating audio files** based on entries from the audio file inventory. Useful during testing.                                                                             |
| `--skip_radio_check`          | **Skip generating radio check** audio clips.                                                                                                                                       |
| `--keep_invalid_files`        | **Keep invalid `.wav` files** around with a modified name instead of deleting them. Useful for debugging and understanding why a file was considered invalid.                      |
| `--max_invalid_attempts`      | Maximum **number of attempts to generate a valid audio file** before giving up. Defaults to 30.                                                                                    |



## 🔄 Common Task: Restart a running crew-chief-autovoicepack container
crew-chief-autovoicepack has mostly [idempotent](https://en.wikipedia.org/wiki/Idempotence) behavior ("can be repeated or retried as often as necessary without causing unintended effects"), so **you are free to start, stop, and restart** the `docker run` or Docker Compose containers at any time.

1. Before generating each voice pack audio file, the generation script checks the output folder to see **if that file already exists, and skips it** if so (unless `--overwrite` is specified).

2. The order of the **phrase inventory entries are randomly shuffled when each container starts** (unless `--original_inventory_order` is specified). In practice, this breaks up the work into uniform chunks that can be run in parallel across multiple containers without needing any coordination beyond checking for file existence in the shared output folder.


## ⏲️ Common Question: How long does it take to generate a voice pack?
**1 to 2 hours** with a modern GPU, 4 to 12 hours with CPU only.

The overall **duration depends** on the number of phrases in the CrewChief phrase inventory (~10,000 by default), the container host machine's CPU/GPU/RAM, whether crew-chief-autovoicepack is running with a GPU or in CPU-only mode, the number of variants (the `--variant_count` parameter), and the number of containers running in parallel.

In general, a single `docker run` container in CPU-only mode will take several minutes to initialize. It should then start generating audio files, with **each new audio file taking a few seconds or less** to create. The total number of these steps can be estimated by the number of phrases in the phrase inventory multiplied by the number of variants.

A 24GB GPU (RTX 4090/3090) will enable [running 8 replicas in parallel](#common-task-running-multiple-containers-in-parallel-to-speed-up-voice-pack-generation), each many times faster than the CPU version. 16GB GPUs (RTX 4080/4070/4060Ti) or lower will support proportionally fewer replicas before being constrained by GPU VRAM. Even with a 8GB GPU and a single container running the audio generation script, **using a GPU will be much faster than the CPU-only mode**.


## 💾 Common Question: How much storage space is used by each voice pack?
A typical `crew-chief-autovoicepack` voice pack using 2 extra variations per original phrase is approximately **2GB**.

The official CrewChief "Jim" audio files are ~0.5GB.

The .wav files generated by `crew-chief-autovoicepack` are (perhaps unnecessarily) larger since they are stored with 32-bit resolution at 24KHz. There are also **many more .wav files in your new voice pack** due to the `--variation_count` parameter, which defaults to 2, but can be set to 0 to disable variations and save storage space, or higher to potentially generate more varied audio at the cost of storage.

The Docker image itself is ~21GB, specifically including large data dependencies in the image, such as a pre-trained text-to-speech model alongside related machine learning frameworks. This avoids having to download these large files (and wait several minutes) each time the container runs.


## 🗑️ Common Question: Can I remove individual audio files from the output folder?
Yes! You are **encouraged to review and curate** the output files (if you have the time/interest) by removing any "bad" ones.

Any **files removed from the voice pack output folder will be regenerated** the next time the `generate_voice_pack.py` script is run, and all the existing files will be (very quickly) skipped.

This allows you to identify and **simply delete any corrupt or poor-quality audio files**, and quickly start the docker container (`docker run ...`) and **run the generate script again** on-demand until you get things perfect.

Note that CrewChief itself **doesn't care how many files are in each folder**, so there is no minimum or maximum. More files just mean **more variety** in the voice pack, as CrewChief will randomly play one of the files from the folder.

Additionally, this means **you can reduce variety by deleting any files you want** as long as there is at least one file left in the folder. If you want to remove a file permanently (including its variants ending in '-1.wav', '-2.wav', etc.) across multiple runs, edit the phrase inventory to remove the corresponding rows entirely.


## ⚠️ Common Question: The logs show a lot of "invalid" files being generated, what's going on?
This is **a side effect of using a generative ML model** to perform the text-to-speech process. Under normal circumstances, the model **output is frequently garbled and unusable** (maybe 10% or more of the time), but by employing a few simple checks on the audio file duration, size, and amount of silence, **crew-chief-autovoicepack will automatically detect the invalid output and regenerate the file up to `--max_invalid_attempts` times** which greatly improves the chances of producing valid, natural-sounding speech.


## 🐳 Common Question: Everyone hates Docker... why is this packaged exclusively as a Docker image??

Docker has a long history of being **a resource hog** with painful installation, configuration, and management, but **the benefits** here are undeniable:

1. **Cross-Platform Consistency**: Enables CrewChief voice pack creation for the widest audience possible, across all operating systems, including cloud servers.
2. **Isolation and Reproducibility**: A Docker image built today will continue to function the same even years from now. This isolation ensures that the environment inside the container doesn't conflict with other software on your machine.
3. **Dependency Management**: It can be nightmarish even for technical users to identify and solve all the Python dependencies and OS packages needed to run advanced machine learning models reliably on their own machines. **I have identified and encapsulated all dependencies** into the crew-chief-autovoicepack Docker image, so you don't have to worry about version conflicts or package management.
4. **Ease of Use**: Docker allows you to **bypass complex setup procedures** (Python virtual environments, installing CUDA for GPU support, etc.), making it easy to run sophisticated software without deep technical knowledge.
5. **Parallelization**: Docker makes it **trivial to run multiple instances in parallel** to speed up computation, especially beneficial to reduce voice pack creation time by 8x or more.
6. **Resource Efficiency**: While Docker does introduce some overhead, it generally runs efficiently, utilizing your system's resources without compromising isolation. **Docker only uses system resources to run the containers you explicitly request**, and will not add extra background processes or slow down your PC when not in use.



## ⚡ Common Task: Running multiple containers in parallel to speed up voice pack generation
To speed up the process of generating a voice pack, you can **run multiple containers in parallel** on the same machine. This is **useful only when using a GPU**, as the CPU-only mode will automatically utilize all available CPU cores, so just use a single container via `docker run` in that case.

Instead of starting a single instance of the Docker container with `docker run ...` you can **use Docker Compose** and the provided `docker-compose.yml` file to **start, stop, and restart multiple containers** at once.

1. Edit the `docker-compose.yml` file to **specify the number of containers** you want to run in parallel ("replicas").
2. Ensure you have downloaded the crew-chief-autovoicepack **Docker image** as mentioned [above](#step-2-download-the-crew-chief-autovoicepack-docker-image-with).
3. **Start the containers** with `docker compose up -d crew-chief-autovoicepack`
4. **Monitor the progress** of the audio generation with `docker compose logs -f`
5. Optionally: **Stop** the containers with `docker compose down`. This will remove all logs and any files saved within the local container filesystem.
6. **Repeat** as needed to generate all the audio files for your voice pack.

NOTE: Annoyingly, there is a difference between `docker-compose` (dash) and `docker compose` (space), based on legacy choices around installing Docker Compose as a plugin versus standalone. `docker compose` is the correct version, and hopefully works for you from the command line ("Command Prompt", "Terminal", etc. depending on your operating system).

If you installed Docker Desktop for Windows or macOS, **you should have `docker compose` available by default**, and will not need to install anything additional.


## 🔍️ Common Question: How do I know it's working/running/progressing?
After starting the container via `docker run ...` and from the shell prompt starting the `generate_voice_pack.py` script, you may see initialization and warning log messages for several minutes, but thereafter should see a stream of **logs indicating the progress** of the audio file generation:

```
Generating audio for 80 - 'right 5' -> 'right 5'
File created at: ./output/Luis/voice/codriver/corner_5_right_reversed/117-a.wav
File created at: ./output/Luis/voice/codriver/corner_5_right_reversed/117-b.wav
File created at: ./output/Luis/voice/codriver/corner_5_right_reversed/117-c.wav
```

These messages will continue until the script has processed all the phrases in the phrase inventory. If you see no messages for a long time, **it is safe to investigate**, including stopping or restarting the container again later (see relevant question elsewhere on this page).

In the example above, it's generating audio files for the 80th phrase in the phrase inventory, out of a total of almost 10,000 phrases. A minor note is that the order of phrase generation is purposefully randomized compared to the original csv file, so "audio file 80" in the example above is not the 80th row in the csv file (search instead for `corner_5_right_reversed` to find the correct row).

When running multiple containers in parallel via `docker compose`, you can **view the logs of all replica containers at once** with `docker compose logs -f` (Ctrl+C to exit).

Based on how quickly these messages are flowing, you can estimate how long the total process will take.

**Bonus** -- Easy ways to gauge the voice pack quality in real-time:
- Manually: Browse the `output` folder, clicking through to each folder and listening to the audio files as they are generated
- Use an audio player that will let you listen to an entire folder tree
- (Linux) Loop over and play each file in the output folder: `find output/Luis/ -type f -name '*.wav' | while read -r file; do echo "$file"; paplay "$file"; done`


## ⏹️ Common Question: If I stop or delete the container, will I lose progress?
No, since you mounted a local folder into the container, **all the generated audio files will be saved** there and will persist even if the container is stopped or deleted. Restart where you left off, or clear the output folder and start fresh.


## 🔁 Common Question: I made a change while the process was running, will it be picked up? What about the previously created audio files?
If you make a change to the `generate_voice_pack.py` script or the `phrase_inventory.csv` file while the process is running, **the changes will not be picked up** until you stop and restart the container (and even in that case, you'll only see changes **if those individual files are directly mounted** into the container overriding the base image's version).

**Rebuilding** the Docker image with `docker build ...` **ensures that your changes are incorporated** into the container, but this may not be necessary for simple changes. Entirely new filenames may need a corresponding `COPY` command in the Dockerfile, for example, if you make a copy of the `phrase_inventory.csv` with a new name. Alternately, you can always mount the new file over the originally expected name, i.e. `docker run ... -v /my_renamed_phrase_inventory.csv:/app/phrase_inventory.csv`


## 🧹 Common Question: I have plenty of disk space, why shouldn't I set variation_count to 25 or more?
Feel free to experiment. I saw diminishing returns after 3-5 variants, as **since the exact text stays the same**, eventually successive attempts will often sound similar enough to one of the previous results that it's not worth the extra storage space.

If you want to add real variety, **consider adding more rows to the phrase inventory**, which is mentioned in detail elsewhere on this page.


## ✍️ Common Question: How can I add my own phrases and commentary to the voice pack?
It's important to realize that **CrewChief has a fixed understanding** of which folders contain the various phrases it will pull from when the conditions arise.

For example, upon noticing a Full-Course Yellow Flag in the sim, CrewChief will decide to play a random selection from the .wav files in the `.../voice/flags/fc_yellow_in_progress_usa` folder.

This corresponds to these rows of the `phrase_inventory.csv` file:

| audio_filename                                 | original_text                              |
|------------------------------------------------|--------------------------------------------|
| `\voice\flags\fc_yellow_in_progress_usa:1.wav` | `we're under caution, the pace car is out` |
| `\voice\flags\fc_yellow_in_progress_usa:2.wav` | `full course yellow, pace car is out`      |
| `\voice\flags\fc_yellow_in_progress_usa:3.wav` | `full course yellow, we're under caution`  |
| `\voice\flags\fc_yellow_in_progress_usa:4.wav` | `full course yellow, pace car is out`      |
| `\voice\flags\fc_yellow_in_progress_usa:5.wav` | `we're under caution, full course yellow`  |
| `\voice\flags\fc_yellow_in_progress_usa:6.wav` | `full course yellow, pace car is out`      |
| `\voice\flags\fc_yellow_in_progress_usa:7.wav` | `we're under caution, full course yellow`  |

Understanding this, **you can add your own phrases** to the voice pack by editing the `phrase_inventory.csv` file based on the existing CrewChief "intents" represented by the folder names in the `audio_filename` column.

**As another example**, if you want to add a new phrase which is played when CrewChief looks for audio intended for `didn't understand`, add a new row to `phrase_inventory.csv` file like this:

| audio_filename                               | original_text                             |
|----------------------------------------------|-------------------------------------------|
| `\voice\acknowledge\didnt_understand:15.wav` | `I have no idea what you're saying, man!` |

...and now **in addition to generating audio clips for the existing 14 official**  `didnt_understand` phrases, `crew-chief-autovoicepack` will also generate a new custom audio clip speaking "I have no idea what you're saying!".

If you don't want some or all of the original phrases, simply remove them. You can even remove (or fail to generate) an entire folder and Crew Chief will just do nothing when triggered with that intent.

Important: You cannot create an entirely new custom phrase (like "That last incident is under investigation") unless it corresponds to an "intention" (folder name in the audio inventory) that CrewChief already recognizes, but you can add an unlimited number and variety of new phrases to any of the existing folders.

Additionally, there is nothing stopping you from cleverly co-opting a certain folder for your own purposes, but the audio will still only be played when CrewChief is triggered by the scenario hinted at by the folder name. i.e. We aren't changing any CrewChief logic, just adding some extra .wav files for it to unknowingly play in the standard situations.

Recommended **places to start**:
- Add a bunch of **custom celebratory messages** to `\voice\lap_counter\finished_race_good_finish`
- Berate your **terrible performance** with new rows for `\voice\lap_counter\finished_race_last`
- In general, start with the same value for the `text_for_tts` and `original_text` columns
- Fix the **bad pronunciation** of your favorite corners in `\voice\corners` by adding a different value for the `text_for_tts` column.


## 📉 Common Question: My generated voice pack sounds a lot worse and has a lot more corrupted audio files than the official repo's voice packs. What will improve my results?
The source of your issues is very likely **from imperfections in the input audio recordings**. You must be comprehensive in **trimming out silence**, and the files must be saved in exactly **the right format** for the coqui xtts model to work effectively.

**Mandatory**:
  1) **10 seconds** or less per clip (longer is ignored)
  2) **25 clips** or less (10 is fine)
  3) WAV file format details: **32-bit** float PCM, **22.5 kHz** sample rate, **mono** channel
  4) Recordings must be **high-quality**, with no background noise, clipping, or distortion
  5) Recordings must be **normalized** to the full dynamic range
  6) Recordings must be **ruthlessly trimmed to remove all silence** at the beginning or end of every file
  7) For any other silence or pauses longer than ~0.5 seconds, **split the clip into two separate clips** at that point and trim the silence away from the start and end
  8) Simply **delete any adversarial** or low-quality clips, as it's usually easier than trying to fix them
  9) **Don't obsess** over capturing the voice in a wide **emotional range**, as the xtts model tends to diminish those aspects anyway. Similarly, be deliberate, but don't worry too much about capturing a specific **phonetic range** -- it's hard to figure out which details will make it into the cloned voice without experimenting.

Other tips:
- Use a modern audio file editor ([ocenaudio](https://www.ocenaudio.com/), Audacity, etc.) to **view the waveform** for each audio clip.
- **Look at the provided voice recordings** in the repo's `baseline` folder for examples of what recorded voice clips should look like.
- The `record_elevenlabs_voice.py` script automatically captures an appropriate number of suitable-length high-quality voice samples, applying suitable audio effects such as normalization, and saving them in the correct format. Use it to **get started quickly**
- **Audio from YouTube** videos (for example, captured from an interview with a tool like [yt-dlp](https://github.com/yt-dlp/yt-dlp)) **is generally usable** after applying ALL the considerations above, but the speaker's voice needs to be 100% isolated with no background noise, music, chatter, etc.
- Recording **your own voice** also works well, when following the guidelines above.


## 🐞 Common Question: How do I report a bug, or ask for more help?
Feel free to **use the "Issues" tab** at the very top of the repo homepage to report any bugs, issues, or feature requests you have. Please include as much detail as possible, including the command you ran, the output you saw, and any relevant context about your system (OS, hardware, etc.).

If you just want **to ask a question, use the "Discussions" tab** instead of "Issues"


## 🤝 Common Question: How do I contribute to the project?
Fork the repo, make your changes, and **submit a pull request**. Please include a detailed description of the changes you made, why you made them, and any relevant context. If you have any questions, feel free to **ask in the "Discussions" tab** at the very top of the repo homepage.


## 🌐 Common Question: How do I create a voice pack in a different language?
I've not done this since I only use English, but here's a rough outline of **suggested steps**:

- **Machine-translate** the `original_text` column of `phrase_inventory.csv` using an LLM like ChatGPT. This can be done iteratively, copy/pasting an acceptable number of rows at a time to the LLM, or fully automated via API calls.
- After translation, **manually review** the csv file in a tool like Excel or LibreOffice Calc
- Manually edit any **incorrect translations**
- Optionally, tweak the **TTS pronunciation** column `text_for_tts` for troublesome entries
- Generate the voice pack **using the normal process**
  - Important: ensure that your updated `phrase_inventory.csv` file is mounted into the container using the `docker run ... -v ...` command line parameter.
  - For example, use `docker run ... -v /path/to/MY_CUSTOM_phrase_inventory.csv:/app/phrase_inventory.csv ...` to override the default phrases with your translated phrases.
- Let the voice pack generate for a few minutes
- Review the output audio files to judge how well it worked

The coqui xtts **model is multilingual and should work well with many languages**, but the quality of the translations will depend on the quality of the machine translation and the quality of the original audio recordings. You may need to experiment with different translation techniques to get the best results, but crew-chief-autovoicepack will still do most of the work -- **imagine having to record and edit ten-thousand audio clips** yourself (you'd need the patience of a Belowski).


## 📤 Common Task: Package a voice pack to share with other users
- **Create** a voice pack (e.g. `Luis`) using the normal process
- **Zip** the entire voice pack folder (e.g. `Luis`) and share it with others

If you have a reason to keep the size of each zip file **below 2GB**, feel free to use the provided `zip_voice_pack.sh` script. This is relevant primarily because the voice pack downloads on this page are hosted by GitHub Releases, which limits files to 2GB or less. Since **you will be providing the download link** from a different provider, you may not have this same requirement, and a single larger file may be more convenient in your case.
```
# if needed, from the root directory of the running container
./zip_voice_pack.sh output/Luis
```

**Want to contribute your new voice pack to the community?**
- Ensure you used something **neutral** like `'Champ'` for the `--your_name` parameter when running `generate_voice_pack.py`. This will prevent your public-facing voice pack from including references to your personal name. Alternatively, just remove the ReplacementRule which adds those references.
- **Zip** the entire voice pack folder (e.g. `output/Luis`)
- **Upload** the zip file to a publicly-accessible location (Google Drive, OneDrive, Dropbox, Mediafire, Mega.nz, etc.)
- Use the **"Issues" tab** at top of this page to create an Issue with an explanation and link to the file.
- I will review and **add the link** to the list of voice packs available for download.


## 🗣️ Common Question: When I use one of the voice packs downloaded from this page, why does the new CrewChief voice have frequent garbled or weird speech output?
Alas, the xtts machine learning model which is performing the text-to-speech work is a "generative" model, which means **its output is not constrained to the exact text we provide**, and it can generate *any* audio data that the model deems as **probabilistically correct** -- even if it's clearly nonsense to a listener.

Improving the quality of the reference audio files used for voice cloning **helps greatly**, but in practice, the best option is simply to **wait for related technology to improve**, then plumb in a more capable and robust text-to-speech tool when available. This is a very active research area with many promising developments in progress.

To mitigate the frequent garbled output, `generate_voice_pack.py` **automatically detects and regenerates suspected invalid audio files**, based on "too long" audio, weird out-of-distribution frequencies, "too much silence", file sizes too large compared to expectations, etc. This makes a big difference.

Similarly, if you had unlimited, cost-free access to the Elevenlabs.io API, you could easily generate even better sounding speech than xtts, with many fewer guardrails and invalid file checks needed.


## 🔊 Common Question: Some of the voice packs seem to have different audio volumes, is this expected?
Yes, **the audio volume level of each voice pack can vary** based on the baseline audio recordings used to create it, as well as due to the processing (especially **dynamic range normalization**). The normalization was done in particular as it made a large difference to the quality of the final TTS output.

The best choice is to **use an audio editing tool to adjust the gain of your baseline recordings** prior to normalizing them. A related solution is to modify the volume of the output voice samples up or down using the `gain` parameter in `generate_voice_pack.py :: apply_audio_effects()`.

Keep in mind that **CrewChief itself has a pretty wide volume range slider** within the app (and the noise of listening environments varies dramatically), so it may not be worth the effort to find a "perfect" volume, but **you will want your generated voice clips to be at a similar volume to the spotter and radio check messages** so that it's comfortable for the listener to hear clips mixed together from both sources.


## 📂 Uncommon Task: Understand the structure of this repo
Most important files:
- `generate_voice_pack.py`: **primary script** which generates the audio files for a new voice pack
- `phrase_inventory.csv`: A comma-separated values (CSV) file that specifies **the phrases to be generated** for the voice pack. Edit/view with a spreadsheet program like Excel or LibreOffice.
- `output/`: folder where the **generated audio files** are saved
- `baseline/`: folder where the **baseline audio recordings** are saved. Pre-populated with an example for `Luis`.

Other supporting files:
- `record_elevenlabs_voice.py`: **generates high-quality baseline recordings** using the Elevenlabs.io API
- `zip_voice_pack.sh`: utility to zip a voice pack folder into **multiple less-than-2GB** files
- `Dockerfile`: The instructions **for building the Docker image** that will run the crew-chief-autovoicepack code
- `docker-compose.yml`: A file that **specifies how to run multiple containers** in parallel to speed up voice pack generation


## 📻 Uncommon Question: My voice pack works, but I don't hear the radio check at startup?
CrewChief has a **common folder for all radio check audio clips**, generally the main `.../sounds/voice/` folder. You will see other radio check folders like `radio_check_Jim`, `radio_check_Mike`, etc. in this folder. If you do not see a folder with the name of your voice pack (like `radio_check_Luis`), it's possible the `radio_check_Luis` folder was not copied into this main folder from the root voice pack folder. **This has to be done manually**, as noted in the [voice pack installation step](#-common-task-add-your-new-voice-pack-to-crewchief).


## 🎛️️ Uncommon Question: Elevenlabs.io audio quality is much better, can I just use that service directly?
Yes! It's easy enough to change the `generate_voice_pack.py` script to use the ElevenLabs.io API to generate high-quality voice recordings. This works fine (with minor additional code) and was the initial approach I took, but it is simply too expensive for the average user as it **requires several hundred dollars** worth of API requests to create a full voice pack.

Consider the **highly-recommended alternate approach** of ["importing" a voice from Elevenlabs.io](#common-task-bootstrap-your-voice-pack-with-an-elevenlabsio-voice-) to serve as a baseline for our unlimited-use local Text-to-Speech engine. This will still create inferior audio files compared to using Elevenlabs directly, but 🤷.


## 🔧 Uncommon Task: Change to a different Text-to-Speech model or service
Replace the `generate_voice_pack.py` function named `generate_speech_coqui_tts()` with a similar function (with a similar signature) which reaches out to the new speech model/service. Now, update any references to the `generate_speech_coqui_tts()` function in the script to call your new function instead.


## 🧑‍💻 Uncommon Task: Recommended developer workflow
- Clone repo locally
- Edit the phrase inventory and/or generate_voice_pack.py as needed
- Rebuild the docker image (see recommended docker commands elsewhere on this page)
- Run the docker image with the output folder mounted to a local folder
- From the container's bash prompt, use the up arrow and select a relevant command line to start with
_ Edit, rebuild, run, over and over while reviewing the output/ dir results


## 💻 Uncommon Question: How much GPU VRAM is required to run the Text-to-Speech process using a GPU?
A "graphics card" (Graphics Processing Unit, or GPU) has memory (Video RAM, or VRAM) which is used by the GPU to store textures, frame buffers, and other data. **Crew-chief-autovoicepack uses a deep learning model** which can utilize your GPU to greatly speed up the text-to-speech process.

**The model requires approximately 2.6GB of VRAM**. If your GPU has 8GB VRAM or more, you will be able to run multiple containers in parallel using the instructions found elsewhere on this page, which will produce your voice pack up to 8x+ faster.


## 🏗️ Uncommon Task: Rebuilding the crew-chief-autovoicepack Docker image
Note that **you can avoid rebuilding the container image** simply by mounting the local version of the files you want to modify in place of the version baked into the container image, such as `generate_voice_pack.py` or `phrase_inventory.csv`. See instructions elsewhere on this page for how to mount a local file into the container.

However, if you make significant changes to the files in the repo, such as modifying the Dockerfile or adding new files, you may prefer to rebuild the Docker image (`docker build ...`).

The process may seem daunting and slow the first time, but it **will complete very quickly each run after the initial build** since Docker caches the intermediate steps. This means you won't have to wait to download the base Linux image, apt packages, pytorch dependencies, ML models, etc. again but you will be able to change the python code and rebuild the image in seconds.

As the repo ages, you may encounter dependency resolution issues or other software supply chain problems, but hopefully are able to work through them with the help of the community or the Internet.

To **build**, from the crew-chief-autovoicepack root folder:
```
> DOCKER_BUILDKIT=1 docker build -f Dockerfile .
```
On Windows, it's easiest to run this from the WSL2 (Linux) bash prompt, but it may also work from the Windows Command Prompt or PowerShell.

If you are using Docker Desktop, you can also see the build process appear on the "Active Builds" tab of "Builds". You can review the progress or check error logs there.

Once the image has been rebuilt, you can run it with `docker run ...` as usual.


## 🖥️ Uncommon Task: Local development without Docker
- Clone the repo locally: `git clone ...`
- Install all necessary OS packages and python dependencies as closely as possible to those **specified in the Dockerfile**
- If using a GPU:
  - Ensure recent nvidia and CUDA drivers
  - Install the Nvidia Container Toolkit (Linux): https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html
  - Optionally, install Deepspeed (recommended)
- Install coqui-tts, **as shown in the Dockerfile**
- Coqui should be operational from the command line:
  - `tts --model_name tts_models/multilingual/multi-dataset/xtts_v2 --speaker_idx 'Claribel Dervla' --language_idx en --use_cuda true --out_path /tmp/x.wav --text 'This is a test.'`


## 🔮 Possible Future Improvements
- Incorporate **RVC (Real Voice Cloning)** to better match the original speaker's voice -- this would take the TTS generated audio and post-process it to sound even more like the original. Could also be applied to the original CrewChief "Jim" voice pack audio to retain the emotional inflection and pacing (though unavoidably inheriting the regional jargon and matey-ness).
- Support creating **new spotter voices**
- Support **alternate text-to-speech services** and models
- Automate **multilingual machine translation** (see ["How do I create a voice pack in a different language?"](#-common-question-how-do-i-create-a-voice-pack-in-a-different-language))


## 📖 References
- **CrewChief**: https://gitlab.com/mr_belowski/CrewChiefV4
- **CrewChief forum** thread on adding new voice packs: https://thecrewchief.org/showthread.php?825-Authoring-alternative-Crew-Chief-voice-packs



<img alt="divider" src="resources/images/divider-1.webp">
