import os
import librosa
import shutil
import numpy as np
from glob import glob
import shutil
from spleeter.separator import Separator
from pydub import AudioSegment
from pydub.utils import mediainfo
import tensorflow as tf
from spleeter.audio.adapter import AudioAdapter

audio_adapter = AudioAdapter.default()

# Function to slice an audio file based on transients using Librosa
def slice_audio_on_transients(file_path, hop_length=512, top_db=20):
    y, sr = librosa.load(file_path, sr=44100)
    onset_frames = librosa.onset.onset_detect(y, sr=sr, hop_length=hop_length, units='frames')
    
    slices = []
    for idx, onset in enumerate(onset_frames):
        start = librosa.frames_to_samples(onset, hop_length=hop_length)
        if idx < len(onset_frames) - 1:
            end = librosa.frames_to_samples(onset_frames[idx + 1], hop_length=hop_length)
        else:
            end = len(y)
        slices.append((start, end))
    
    return slices

# Function to separate audio stems using Spleeter
def separate_audio_stems(file_path, output_folder):
    separator = Separator('spleeter:4stems', multiprocess=False)
    separator.separate_to_file(file_path, output_folder, audio_adapter=audio_adapter, codec='wav', bitrate='1411k')

# Function to create a folder structure
def create_folder_structure(base_path, category):
    folder_path = os.path.join(base_path, category)
    os.makedirs(folder_path, exist_ok=True)
    return folder_path

# Function to check dB level of audio file
def check_low_db_level(file_path, threshold_db=-40):
    file_format = mediainfo(file_path)['format_name']
    with open(file_path, 'rb') as file_handle:
        audio = AudioSegment.from_file(file_handle, format=file_format)
    return audio.dBFS < threshold_db

def detect_tempo(file_path):
    y, sr = librosa.load(file_path, sr=None)

    print(f"Loaded audio for tempo detection: {file_path}, length={len(y)}, sr={sr}")
    
    if len(y) == 0:
        return 0

    tempo, _ = librosa.beat.beat_track(y, sr=sr)
    return round(tempo)

def detect_key(file_path):
    y, sr = librosa.load(file_path, sr=None)

    print(f"Loaded audio for key detection: {file_path}, length={len(y)}, sr={sr}")
    
    if len(y) == 0:
        return '0A'

    chroma = librosa.feature.chroma_stft(y, sr=sr)
    return estimate_key(chroma)

def estimate_key(chroma):
    key_templates = librosa.filters.chroma(sr=44100, n_fft=2048)
    correlation = np.dot(chroma.T, key_templates)
    key_mode = np.argmax(np.mean(correlation, axis=0))
    key_idx = key_mode % 12
    mode = key_mode // 12

    camelot_major = ['8B', '3B', '10B', '5B', '12B', '7B', '2B', '9B', '4B', '11B', '6B', '1B']
    camelot_minor = ['5A', '12A', '7A', '2A', '9A', '4A', '11A', '6A', '1A', '8A', '3A', '10A']
    camelot_wheel = camelot_minor if mode == 1 else camelot_major
    camelot_key = camelot_wheel[key_idx]
    return camelot_key

def is_empty_slice(start, end):
    return end - start <= 0

def clean_up(folder_path):
    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print(f"Failed to delete {file_path}. Reason: {e}")

def main():
    # Source folder containing your FLAC files
    source_folder = "input_flac_files"

    # Process each FLAC file in the source folder
    for file_name in os.listdir(source_folder):
        if file_name.lower().endswith('.flac'):
            input_file = os.path.join(source_folder, file_name)

            unique_file_counter = 0

            print(f"Processing file: {file_name}")

            # Get input file format
            input_file_format = mediainfo(input_file)['format_name']

            # Load the input audio file using pydub
            with open(input_file, 'rb') as file_handle:
                audio = AudioSegment.from_file(file_handle, format=input_file_format)

            # Output folders
            output_folder = os.path.join("output_slices", file_name[:-5])
            output_stems_folder = os.path.join("output_stems", file_name[:-5])

            # Create output folders if they don't exist
            os.makedirs(output_folder, exist_ok=True)
            os.makedirs(output_stems_folder, exist_ok=True)

            # Slice the audio based on transients
            audio_slices = slice_audio_on_transients(input_file)

            # Process audio slices in batches of 5
            for batch_idx in range(0, len(audio_slices), 5):
                batch_slices = audio_slices[batch_idx:batch_idx + 5]
                batch_folder = os.path.join(output_folder, f"batch{batch_idx//5}")
                os.makedirs(batch_folder, exist_ok=True)

                # Iterate through the audio slices in the batch and export them to a folder
                for idx, (start, end) in enumerate(batch_slices):
                    if end > len(audio):
                        break
                    slice_audio = audio[start:end]
                    slice_file_name = f'slice_{batch_idx+idx:03d}.wav'
                    slice_file_path = os.path.join(batch_folder, slice_file_name)
                    slice_audio.export(slice_file_path, format='wav')

                    # Separate the audio stems using Spleeter
                    separate_audio_stems(slice_file_path, output_stems_folder)
                    tf.keras.backend.clear_session()  # Clear TensorFlow session
                # Organize separated stems into folders
                stems = ['vocals', 'drums', 'bass', 'other']
                for stem in stems:
                    stem_folder = os.path.join("samples", stem)
                    os.makedirs(stem_folder, exist_ok=True)

                    stem_files = [y for x in os.walk(output_stems_folder) for y in glob(os.path.join(x[0], f'{stem}.wav'))]

                    for file_name in stem_files:

                        y, sr = librosa.load(file_name, sr=None)
                        if len(y) == 0:
                            print(f"Skipping empty audio file: {file_name}")
                            os.remove(file_name)
                        else:

                            key        = detect_key(file_name)
                            tempo      = detect_tempo(file_name)
                            file_parts = input_file.split(" - ")

                            if len(file_parts) >= 3:
                                full_artist = file_parts[1]
                                full_title = file_parts[-1]
                            else:
                                full_artist = "Unknown"
                                full_title = "Unknown"

                            artist = full_artist.split(" ")[0]
                            track = full_title.split(" ")[0].split(".")[0]

                            if check_low_db_level(file_name):
                                os.remove(file_name)
                            else:
                                dest_file_name = f'{key}-{tempo}-{artist}-{track}-{stem}{unique_file_counter:03d}.wav'
                                dest_file_path = os.path.join(stem_folder, dest_file_name)
                                unique_file_counter += 1
                                shutil.move(file_name, dest_file_path)
            os.remove(input_file)
        clean_up("output_stems")
        clean_up("output_slices")

if __name__ == "__main__":
    main()