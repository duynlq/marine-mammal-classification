import os
from pydub import AudioSegment
from pydub.utils import make_chunks
import random


def chunk30Augment():

    # MANUALLY EDIT CLASS NAMES
    mammalName = "White-sided Dolphin"

    path = "data/"
    train_path = "training_data/"
    chunk_len = 30000  # 30 seconds

    for file in os.listdir(path+mammalName):

        # Ensure audio files ONLY
        if not file.endswith((".wav", ".mp3", ".flac")):
            continue

        # Prepare audio files into Python
        file_path = os.path.join(path, mammalName, file)
        sound = AudioSegment.from_file(file_path)

        # Extract file name without extension
        file_name, _ = os.path.splitext(file)

        # If audio is less than 30s, loop until at least 30s
        while len(sound) < chunk_len:
            # Concatenate to itself
            sound += sound
            # Trim exactly to 30s (in case duplication exceeds 30s)
            sound = sound[:chunk_len]

        # Ensure we don't lose the remainder
        chunks = make_chunks(sound, chunk_len)
        for idx, chunk in enumerate(chunks):
            os.makedirs(train_path+mammalName, exist_ok=True)
            chunk.export(f"{train_path}{mammalName}/{file_name}-{idx+1}.wav", format="wav")

        for idx, sound in enumerate(chunks):
            # randomly +/- 2 semitones
            octaves = random.choice([0.1667, -0.1667])
            new_sample_rate = int(sound.frame_rate * (2.0 ** octaves))
            new_sound = sound._spawn(sound.raw_data, overrides={'frame_rate': new_sample_rate})

            print(file_name)
            # randomly +/- 3 dB
            dB = random.choice([3, -3])
            # Calculate half duration dynamically
            half_duration = len(new_sound) // 2  # Half of total duration
            # grab the first 15 and last 15 and concat
            first = new_sound[:half_duration]
            last = new_sound[-half_duration:]
            aug_samp = first + last
            aug_samp = aug_samp + dB

            # export augmented audio into its appropriate class
            aug_samp.export(f"{train_path}{mammalName}/{file_name}-{idx+1}aug.wav", format="wav")


if __name__ == "__main__":

    chunk30Augment()
