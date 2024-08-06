from pydub import AudioSegment
import numpy as np


def generate_noise(duration_ms, sample_rate, noise_type="white"):
    duration_s = duration_ms / 1000
    num_samples = int(sample_rate * duration_s)

    if noise_type == "white":
        noise = np.random.normal(0, 1, num_samples)
    elif noise_type == "pink":
        num_columns = 16
        array = np.random.randn(num_columns, num_samples)
        noise = np.zeros(num_samples)
        for i in range(num_samples):
            noise[i] = np.sum(array[:, i]) / np.sqrt(num_columns)
    elif noise_type == "brown":
        noise = np.cumsum(np.random.randn(num_samples))
        noise = noise / np.max(np.abs(noise))
    else:
        raise ValueError("Unsupported noise type")

    noise = np.int16(noise / np.max(np.abs(noise)) * 32767)
    return noise


def array_to_audio_segment(noise_array, sample_rate):
    return AudioSegment(
        noise_array.tobytes(),
        frame_rate=sample_rate,
        sample_width=noise_array.dtype.itemsize,
        channels=1,
    )


def apply_effects(input_file, output_file):
    audio = AudioSegment.from_file(input_file)
    sample_rate = audio.frame_rate
    duration_ms = len(audio)

    print("Original audio duration (ms):", duration_ms)
    print("Sample rate:", sample_rate)

    # Apply initial compression and equalization (if necessary)
    audio = audio.low_pass_filter(100)
    audio = audio.high_pass_filter(100)

    # Generate and overlay noise segments with very low levels
    white_noise = generate_noise(duration_ms, sample_rate, noise_type="white")
    pink_noise = generate_noise(duration_ms, sample_rate, noise_type="pink")
    brown_noise = generate_noise(duration_ms, sample_rate, noise_type="brown")

    white_noise_segment = array_to_audio_segment(white_noise, sample_rate).apply_gain(
        -50
    )
    pink_noise_segment = array_to_audio_segment(pink_noise, sample_rate).apply_gain(-50)
    brown_noise_segment = array_to_audio_segment(brown_noise, sample_rate).apply_gain(
        -70
    )

    print("White noise segment duration (ms):", len(white_noise_segment))
    print("Pink noise segment duration (ms):", len(pink_noise_segment))
    print("Brown noise segment duration (ms):", len(brown_noise_segment))

    noise_segment = white_noise_segment.overlay(pink_noise_segment).overlay(
        brown_noise_segment
    )
    combined_audio = audio.overlay(noise_segment)

    print("Combined audio duration (ms):", len(combined_audio))

    # Normalize to ensure full dynamic range
    combined_audio = combined_audio.normalize()

    print("Final audio duration (ms):", len(combined_audio))

    combined_audio.export(output_file, format="wav")


apply_effects("noise_test.wav", "noise_test_output.wav")
