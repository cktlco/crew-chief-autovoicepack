

### Coqui TTS
- must install nvidia container toolkit if using GPU on linux: https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html


### Alltalk Beta
https://github.com/erew123/alltalk_tts/tree/alltalkbeta

### how to mount a custom audio inventory file
docker run -v /path/to/local/file:/path/in/container/file <image_name>

### known issues
- occasional garbled or corrupt audio (a few percent of the total)


### References
- CrewChief: https://gitlab.com/mr_belowski/CrewChiefV4
- CrewChief official thread on adding new voice packs: https://thecrewchief.org/showthread.php?825-Authoring-alternative-Crew-Chief-voice-packs
