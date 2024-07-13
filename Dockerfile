# run with something like:
# docker run -it --rm -p 7518:7518 -p 7851:7851 --gpus all crew-chief-autovoicepack:v0.1

FROM nvidia/cuda:12.4.0-runtime-ubuntu22.04

WORKDIR /app

## Set the working directory in the container
#WORKDIR /app
#
## Set environment variable for non-interactive installation
#ENV DEBIAN_FRONTEND=noninteractive
#
## Install necessary system packages and expect
#RUN apt-get update && \
#    apt-get install -y curl git espeak-ng && \
#    apt-get clean

## Clone the repository
#RUN git clone -b alltalkbeta https://github.com/erew123/alltalk_tts
#
## Copy the custom setup script into the container
#COPY dockerfile_alltalk_setup.sh /app/alltalk_tts/dockerfile_alltalk_setup.sh
#COPY dockerfile_start_alltalk.py /app/alltalk_tts/dockerfile_start_alltalk.sh
#
## Change directory to the cloned repository
#WORKDIR /app/alltalk_tts
#
## Ensure the setup script is executable
#RUN chmod +x dockerfile_alltalk_setup.sh
#
## Run the alltalk install script
#RUN ./dockerfile_alltalk_setup.sh
#
## Ensure the start_alltalk.sh script is executable
#RUN chmod +x dockerfile_start_alltalk.py start_environment.sh
#
## Activate the Conda environment and install a few extra dependencies using pip
#RUN /bin/bash -c "source /opt/conda/etc/profile.d/conda.sh && conda activate /app/alltalk_tts/alltalk_environment/env && pip install soundfile inputimeout"
#
## Run the AllTalk server
#CMD ["bash"]
##CMD ["bash", "-c", "source /opt/conda/etc/profile.d/conda.sh && conda activate /app/alltalk_tts/alltalk_environment/env && ./dockerfile_start_alltalk.py"]

RUN apt-get update
RUN apt-get install -y --no-install-recommends gcc g++ make curl python3 python3-dev python3-pip python3-venv python3-wheel espeak-ng libsndfile1-dev && rm -rf /var/lib/apt/lists/*
RUN pip3 install llvmlite --ignore-installed

RUN pip3 install torch torchaudio --extra-index-url https://download.pytorch.org/whl/cu125
RUN rm -rf /root/.cache/pip

RUN pip install coqui-tts

# run text-to-speech once so the model is downloaded into the docker image
# note this particular model is retricted to non-commercial use
# xtts: https://coqui-tts.readthedocs.io/en/latest/models/xtts.html
RUN yes y | tts --model_name tts_models/multilingual/multi-dataset/xtts_v2 --text "Downloading model." --speaker_idx "Ana Florence" --language_idx en

#RUN pip install deepspeed==0.10.3

COPY generate_voice_pack.py .
COPY transcript.csv .
COPY recordings/ .

# add some canned command lines to the shell history for easy access
RUN echo "tts --model_name tts_models/multilingual/multi-dataset/xtts_v2 --speaker_idx 'Claribel Dervla' --language_idx en --use_cuda true --out_path /tmp/x.wav --text ''" >> ~/.bash_history
#RUN echo "tts --model_name tts_models/multilingual/multi-dataset/xtts_v2 --list_speaker_idx &> /tmp/speakers && cat /tmp/speakers | grep gpt_cond" >> ~/.bash_history
RUN echo "python3 generate_voice_pack.py" >> ~/.bash_history

CMD ["bash"]