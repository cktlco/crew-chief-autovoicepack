# Build this image with Buildkit enabled:
#   DOCKER_BUILDKIT=1 docker build -t crew-chief-autovoicepack:v0.1 .

# Run with something like:
#    docker run --rm -it --gpus all --name crew-chief-autovoicepack -v /MY_DISK/crew-chief-autovoicepack/output:/app/output crew-chief-autovoicepack:v0.1
#
# or in Windows, run with Docker Desktop *making sure to mount the container's
# /app/output directory to a directory on your local disk* -- otherwise, you'll
# have to manually copy the generated wav files out of the container

# This image is fully-compatible with non-GPU systems, operations will just fall back to the CPU
FROM nvidia/cuda:12.6.0-base-ubuntu22.04 AS builder
#
#WORKDIR /app
#
## Notable OS dependencies:
## - espeak-ng, libsndfile1-dev are OS-level dependencies for the coqui TTS application
## - git Large File Support (LFS) is needed to download the xtts text-to-speech model from huggingface. Note that this is saved into the Docker image filesystem, not downloaded at runtime.
## - ffmpeg, sox are needed for audio processing (mp3 to wav conversion, silence trimming)
#ENV DEBIAN_FRONTEND=noninteractive
#RUN apt-get -qq update && apt-get -qq install -y --no-install-recommends gcc g++ make curl python3 python3-dev python3-pip python3-venv python3-wheel wget espeak-ng libsndfile1-dev ca-certificates gnupg git git-lfs ffmpeg sox iputils-ping telnet vim > /dev/null && rm -rf /var/lib/apt/lists/* && apt-get -qq clean && rm -rf /root/.cache/pip
#
## Install nvidia CUDA Toolkit (includes nvcc needed by deepspeed)
#RUN wget https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2204/x86_64/cuda-ubuntu2204.pin \
#    && mv cuda-ubuntu2204.pin /etc/apt/preferences.d/cuda-repository-pin-600 \
#    && wget -q https://developer.download.nvidia.com/compute/cuda/12.6.2/local_installers/cuda-repo-ubuntu2204-12-6-local_12.6.2-560.35.03-1_amd64.deb \
#    && dpkg -i cuda-repo-ubuntu2204-12-6-local_12.6.2-560.35.03-1_amd64.deb > /dev/null \
#    && cp /var/cuda-repo-ubuntu2204-12-6-local/cuda-*-keyring.gpg /usr/share/keyrings/ \
#    && apt-get update > /dev/null \
#    && apt-get -q install -y --no-install-recommends \
#    cuda-toolkit-12-6 > /dev/null \
#    && rm -rf /var/lib/apt/lists/* && apt-get clean && rm -rf /tmp/* /var/tmp/* \
#    && rm -rf /app/cuda-repo* /var/cuda-repo* \
#    && rm -rf /opt/nvidia/nsight-compute /opt/nvidia/nsight-systems
#
#FROM builder
#
## CUDA env vars
#ENV PATH=/usr/local/cuda-12.6/bin:${PATH}
#ENV LD_LIBRARY_PATH=/usr/local/cuda-12.6/lib64:${LD_LIBRARY_PATH}
#
## git Large File Support
#RUN git lfs install
#
## LLVM is required by deepspeed
#RUN pip3 --no-cache-dir install llvmlite --ignore-installed
#
## Install pytorch
#RUN pip3 --no-cache-dir install torch torchaudio --extra-index-url https://download.pytorch.org/whl/cu126
#
## Install coqui-tts python package (framework which runs the text-to-speech model)
#RUN pip --no-cache-dir install coqui-tts
#
## Download the 1.5GB xtts model weights from huggingface, save into the Docker image filesystem
## This is the slowest step in the build process, but will be cached for future builds
#RUN git clone --branch v2.0.3 https://huggingface.co/coqui/XTTS-v2 /app/data/tts_models--multilingual--multi-dataset--xtts_v2 \
#    && rm -rf /app/data/tts_models--multilingual--multi-dataset--xtts_v2/.git \
#    && mkdir -p /root/.local/share/tts \
#    && ln -s /app/data/tts_models--multilingual--multi-dataset--xtts_v2 /root/.local/share/tts/tts_models--multilingual--multi-dataset--xtts_v2
#
## Deepspeed is optional and requires a CUDA GPU, but greatly speeds up text-to-speech generation
#RUN pip --no-cache-dir install deepspeed
#
## Copy the Python scripts, data files, and baseline recording into the Docker image
#COPY generate_voice_pack.py utils.py record_elevenlabs_voice.py zip_voice_pack.py phrase_inventory.csv translate_phrases.py ./
#COPY baseline/Luis ./baseline/Luis/
#
## Customize shell prompt and add canned command lines to the shell history
#RUN echo 'export PS1="crew-chief-autovoicepack > "' >> /root/.bashrc && \
#    echo "python3 translate_phrases.py --target_language German --translated_phrase_inventory phrase_inventory_de.csv" >> ~/.bash_history && \
#    echo "python3 record_elevenlabs_voice.py --voice_name XXX --voice_id XXX" >> ~/.bash_history && \
#    echo "python3 generate_voice_pack.py --your_name 'Sieger' --voice_name 'Luis_de' --tts_voice_name 'Looees' --phrase_inventory phrase_inventory_de.csv --variation_count 1" >> ~/.bash_history && \
#    echo "python3 generate_voice_pack.py --your_name 'Champ' --voice_name 'Luis'" >> ~/.bash_history

# Sit at a bash prompt when the container starts
# (use up-arrow to browse some suggested command lines)
CMD ["bash"]