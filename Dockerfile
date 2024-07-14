# build this image with Buildkit enabled:
# DOCKER_BUILDKIT=1 docker build -t crew-chief-autovoicepack:v0.1 .

# run with something like:
# docker run -it --rm -p 7518:7518 -p 7851:7851 --gpus all crew-chief-autovoicepack:v0.1

FROM nvidia/cuda:12.4.0-devel-ubuntu22.04

WORKDIR /app

RUN apt-get update
RUN apt-get install -y --no-install-recommends gcc g++ make curl python3 python3-dev python3-pip python3-venv python3-wheel espeak-ng libsndfile1-dev git git-lfs && rm -rf /var/lib/apt/lists/* && apt-get clean

# git lfs is needed to download the full file content during git clone
RUN git lfs install

RUN pip3 install llvmlite --ignore-installed

RUN pip3 install torch torchaudio --extra-index-url https://download.pytorch.org/whl/cu125
RUN rm -rf /root/.cache/pip

RUN pip install coqui-tts

# run text-to-speech once so the model is downloaded into the docker image
# note this particular model is retricted to non-commercial use
# xtts: https://coqui-tts.readthedocs.io/en/latest/models/xtts.html
#RUN yes y | tts --model_name tts_models/multilingual/multi-dataset/xtts_v2 --text "Downloading model." --speaker_idx "Ana Florence" --language_idx en

# download the xtts model
RUN git clone --branch v2.0.3 https://huggingface.co/coqui/XTTS-v2 /root/.local/share/tts/tts_models--multilingual--multi-dataset--xtts_v2

RUN pip install deepspeed

COPY generate_voice_pack.py .
COPY transcript.csv .
COPY recordings/ .

# add some canned command lines to the shell history for easy access
RUN echo "tts --model_name tts_models/multilingual/multi-dataset/xtts_v2 --list_speaker_idx &> /tmp/speakers && cat /tmp/speakers | grep gpt_cond" >> ~/.bash_history
RUN echo "tts --model_name tts_models/multilingual/multi-dataset/xtts_v2 --speaker_idx 'Claribel Dervla' --language_idx en --use_cuda true --out_path /tmp/x.wav --text 'I will cause trouble.'" >> ~/.bash_history
RUN echo "python3 generate_voice_pack.py" >> ~/.bash_history

CMD ["bash"]