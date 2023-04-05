# Sample Creator

Sample Creator is a Python-based script for processing FLAC audio files to generate sliced samples with metadata for use in music production. It utilizes libraries such as Spleeter, Librosa, and PyDub to extract stems, detect tempo and key, and slice the audio based on transients.

## Requirements

- Python 3.9 or higher
- Spleeter
- Librosa
- NumPy
- PyDub
- TensorFlow
- ffmpeg

To install the required packages, run:

```bash
pip install spleeter librosa numpy pydub tensorflow
```

For installing ffmpeg, please follow the instructions for your specific operating system.

## Usage
Clone the repository:

```bash
git clone https://github.com/christian-bell/sample_creator.git
```

Add your input FLAC files to the input_flac_files folder.

Run the split_samples.py script:

```bash
python split_samples.py
```

Once the script has finished processing the files, the sliced samples and metadata will be available in the samples folder organized by stem type (vocals, drums, bass, other).


Example input .flac file: "04 - Sofia Kourtesis - La Perla.flac"
Example sample output based on example input file: 1B-89-Sofia-La-other023.wav, 1B-89-Sofia-La-drums023.wav

Adjustments would need to be made to account for different input file formats.
