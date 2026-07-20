#analyzer.py

# import dialog window for file selection
from tkinter import filedialog
# import warning window
from tkinter.messagebox import showwarning
# import library for working with mp3 files
import librosa
# import library for visualization and plotting
import matplotlib.pyplot as plt
# import library for working with matrices
import numpy as np


class MusicAnalyzer:
    def __init__(self):

        # Constants for key detection
        self.NOTES = ('C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B')
        # Step weights for major (Albrecht-Shmulevich Major)
        self.MAJOR_PROFILE = [6.51, 1.05, 3.54, 1.15, 4.39, 3.55, 1.01, 5.06, 1.05, 3.49, 1.15, 2.21]
        # Step weights for minor (Albrecht-Shmulevich Minor)
        self.MINOR_PROFILE = [6.45, 1.10, 2.81, 5.23, 1.09, 3.37, 1.05, 4.86, 3.43, 1.10, 2.30, 2.02]

        self.path_mp3 = None
        self.y = None
        self.sr = None
        self.tempo = None
        self.duration = None
        self.key = None

        self.rms = None
        self.sc = None
        self.zcr = None

    def detect_key(self):
        """
        Determines the track key using the Krumhansl-Schmuckler algorithm.
        Compares the chromagram with Albrecht-Shmulevich profiles using Pearson correlation.

        Returns:
            str: Key (e.g., "C Major" or "A Minor")
        """

        # Track chromagram with averaged note energies
        # I.e., averaged row-wise from the original chromagram matrix of 12 x N, where 12 rows = 12 notes
        # N = columns, frames (audio chunks)
        chroma_mean = librosa.feature.chroma_cqt(y=self.y, sr=self.sr).mean(axis=1)

        # Dictionary to store key-correlation pairs
        correlation_dict = {}

        # Find correlation with all keys
        for i in range(12):
            rolled_major_profile = np.roll(self.MAJOR_PROFILE, i)
            correlation_dict[self.NOTES[i] + ' Major'] = np.corrcoef(rolled_major_profile, chroma_mean)[0][1]

            rolled_minor_profile = np.roll(self.MINOR_PROFILE, i)
            correlation_dict[self.NOTES[i] + ' Minor'] = np.corrcoef(rolled_minor_profile, chroma_mean)[0][1]

        return max(correlation_dict, key=correlation_dict.get)


    def load_mp3(self):
        """
        Loads an MP3 file via a dialog window and calculates all metrics.
        Shows a warning and resets data on error.
        """
        # Open dialog, load audio, calculate metrics
        # Save everything to self.y, self.sr, self.rms, etc.

        # Assign the file path to the variable
        self.path_mp3 = filedialog.askopenfilename(filetypes=[("MP3 Audio Files", "*.mp3")])

        # If no file is selected (no path), show a warning window
        if not self.path_mp3:
            showwarning(title='Warning!', message='You did not select a file')
            self.y = None
            return None

        # If everything is OK (file selected, path exists)
        else:
            try:
                # Load audio
                self.y, self.sr = librosa.load(self.path_mp3)

                # Calculate track duration
                self.duration = librosa.get_duration(y=self.y, sr=self.sr)

                # Tempo
                self.tempo = librosa.beat.tempo(y=self.y, sr=self.sr)

                # Key
                self.key = self.detect_key()

                # Calculate RMS (Root Mean Square) — "loudness" of the sound at each moment
                self.rms = librosa.feature.rms(y=self.y)[0]

                # Spectral Centroid — "brightness" of the sound.
                # High centroid = "bright", "shimmering" sound (e.g., cymbals, flute)
                # Low centroid = "dark", "bassy" sound (e.g., kick drum, bass guitar)
                # Value in Hertz (Hz), typically from 500 to 5000
                self.sc = librosa.feature.spectral_centroid(y=self.y, sr=self.sr)[0]

                # Zero Crossing Rate (ZCR) — "percussiveness" of the sound.
                # Shows how often the sound wave crosses zero
                # High ZCR = "noisy", "harsh" sound (e.g., hi-hat, noise)
                # Low ZCR = "smooth", "clean" sound (e.g., sine wave)
                # Value from 0 to 1
                self.zcr = librosa.feature.zero_crossing_rate(self.y)[0]

                # Output to label
                report = {
                    "path": self.path_mp3,
                    "duration": round(self.duration, 1),
                    "tempo": int(self.tempo[0]),
                    "key": self.key,
                    "sample_rate": self.sr
                }

                return report

            except Exception as e:

                # If something went wrong — show a user-friendly message
                showwarning(title='Error', message=f'Failed to load file:\n{str(e)}')
                # Reset data so graphs cannot be plotted
                self.y = None

    def analyze(self):
        """
        Plots RMS, Spectral Centroid, and ZCR graphs in a single window.
        Shows a warning if no data is loaded.
        """
        # Check if data exists (self.y is not None)
        # If yes — plot graphs
        # If no — show warning
        if self.y is None:
            showwarning(title='Warning', message="Please load a file first")
        else:
            # Calculate time axis ONCE
            times = librosa.times_like(self.rms, sr=self.sr)

            # Create a 3x1 grid (3 rows, 1 column)
            plt.figure(figsize=(10, 8))

            # 1. RMS graph
            plt.subplot(3, 1, 1)
            plt.plot(times, self.rms, color='blue')
            plt.title('RMS (Loudness)')
            plt.ylabel('Amplitude')

            # 2. Spectral Centroid graph
            plt.subplot(3, 1, 2)
            plt.plot(times, self.sc, color='green')
            plt.title('Spectral Centroid (Brightness)')
            plt.ylabel('Frequency, Hz')

            # 3. ZCR graph
            plt.subplot(3, 1, 3)
            plt.plot(times, self.zcr, color='red')
            plt.title('Zero Crossing Rate (Percussiveness)')
            plt.ylabel('Ratio')
            plt.xlabel('Time, sec')

            plt.tight_layout()
            plt.show()