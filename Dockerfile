# Build this image with Buildkit enabled:
#   DOCKER_BUILDKIT=1 docker build -t crew-chief-autovoicepack:v0.1 .

# Run with something like:
#    docker run --rm -it --gpus all --name crew-chief-autovoicepack -v /MY_DISK/crew-chief-autovoicepack/output:/app/output crew-chief-autovoicepack:v0.1
#
# or in Windows, run with Docker Desktop *making sure to mount the container's
# /app/output directory to a directory on your local disk* -- otherwise, you'll
# have to manually copy the generated wav files out of the container

# Use a "devel" version of the CUDA image since deepspeed needs nvcc for runtime kernel compilation
# This image is fully-compatible with non-GPU systems, operations will just fall back to the CPU
FROM nvidia/cuda:12.4.0-devel-ubuntu22.04

WORKDIR /app

# Notable OS dependencies:
# - espeak-ng, libsndfile1-dev are OS-level dependencies for the coqui TTS application
# - git Large File Support (LFS) is needed to download the xtts text-to-speech model from huggingface. Note that this is saved into the Docker image filesystem, not downloaded at runtime.
# - ffmpeg, sox are needed for audio processing (mp3 to wav conversion, silence trimming)
RUN apt-get update && apt-get install -y --no-install-recommends gcc g++ make curl python3 python3-dev python3-pip python3-venv python3-wheel espeak-ng libsndfile1-dev git git-lfs ffmpeg sox && rm -rf /var/lib/apt/lists/* && apt-get clean

# git Large File Support
RUN git lfs install

# LLVM is required by deepspeed
RUN pip3 install llvmlite --ignore-installed

# Install pytorch
RUN pip3 install torch torchaudio --extra-index-url https://download.pytorch.org/whl/cu125

# Remove pip python package manager cache to save space
RUN rm -rf /root/.cache/pip

# Install coqui-tts python package (framework which runs the text-to-speech model)
RUN pip install coqui-tts

# Download the 1.5GB xtts model weights from huggingface, save into the Docker image filesystem
# This is the slowest step in the build process, but will be cached for future builds
RUN git clone --branch v2.0.3 https://huggingface.co/coqui/XTTS-v2 /root/.local/share/tts/tts_models--multilingual--multi-dataset--xtts_v2

# Deepspeed is optional and requires a CUDA GPU, but greatly speeds up text-to-speech generation
RUN pip install deepspeed

# Copy the python scripts and data files into the Docker image
COPY generate_voice_pack.py .
COPY record_elevenlabs_voice.py .
COPY zip_voice_pack.py .
COPY phrase_inventory.csv .
# Copy an example baseline recording
COPY baseline/Luis baseline/Luis

# Make the shell prompt more friendly
RUN echo 'export PS1="crew-chief-autovoicepack > "' >> /root/.bashrc

# Add some canned command lines to the shell history for convenience
RUN echo "python3 record_elevenlabs_voice.py --voice_name XXX --voice_id XXX" >> ~/.bash_history
RUN echo "python3 generate_voice_pack.py --your_name '' --voice_name ''" >> ~/.bash_history

# Sit at a bash prompt when the container starts
# (use up-arrow to browse some suggested command lines)
CMD ["bash"]