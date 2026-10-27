#analyzer.py

# import dialog window for file selection
from tkinter import filedialog

# import warning and error windows
from tkinter.messagebox import showwarning, showerror

# import library for working with matrices
import numpy as np

# Heavy libraries (librosa, matplotlib) are imported lazily by preload_libs(),
# so the window can appear immediately while they load in a background thread.
# import library for working with mp3 files
librosa = None
# import library for visualization and plotting
plt = None


def preload_libs():
    """
    Imports the heavy libraries (librosa, matplotlib) and warms up numba-compiled functions.
    Meant to be run in a background thread at application startup.
    """
    global librosa, plt

    import librosa as _librosa
    import matplotlib.pyplot as _plt

    librosa, plt = _librosa, _plt

    # Warm-up: the first call of some librosa functions triggers numba compilation,
    # so run them once on a short silent signal. Failure here is not critical.
    try:
        warm_y = np.zeros(22050, dtype=np.float32)
        librosa.feature.chroma_cqt(y=warm_y, sr=22050)
        librosa.feature.spectral_centroid(y=warm_y, sr=22050)
    except Exception:
        pass


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

    def detect_key(self, y, sr):
        """
        Determines the track key using the Krumhansl-Schmuckler algorithm.
        Compares the chromagram with Albrecht-Shmulevich profiles using Pearson correlation.

        Args:
            y: audio time series
            sr: sampling rate of y

        Returns:
            str: Key (e.g., "C Major" or "A Minor")
        """

        # Track chromagram with averaged note energies
        # I.e., averaged row-wise from the original chromagram matrix of 12 x N, where 12 rows = 12 notes
        # N = columns, frames (audio chunks)
        chroma_mean = librosa.feature.chroma_cqt(y=y, sr=sr).mean(axis=1)

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
        If the dialog is cancelled, nothing happens and previously loaded data is kept.
        Shows an error window on failure; previously loaded data is also kept.
        """

        # Open dialog, load audio, calculate metrics
        # Save everything to self.y, self.sr, self.rms, etc. (only if everything succeeded)

        # Assign the file path to a local variable
        path = filedialog.askopenfilename(filetypes=[("MP3 Audio Files", "*.mp3")])

        # If no file is selected (no path), cancelling is not an error:
        # just exit and keep the previously loaded data untouched
        if not path:
            return None

        try:
            # Everything is calculated into local variables first,
            # so a failure in the middle cannot leave the object half-updated

            # Load audio
            y, sr = librosa.load(path)

            # Calculate track duration
            duration = librosa.get_duration(y=y, sr=sr)

            # Tempo
            tempo = librosa.beat.tempo(y=y, sr=sr)

            # Key
            key = self.detect_key(y, sr)

            # Calculate RMS (Root Mean Square) — "loudness" of the sound at each moment
            rms = librosa.feature.rms(y=y)[0]

            # Spectral Centroid — "brightness" of the sound.
            # High centroid = "bright", "shimmering" sound (e.g., cymbals, flute)
            # Low centroid = "dark", "bassy" sound (e.g., kick drum, bass guitar)
            # Value in Hertz (Hz), typically from 500 to 5000
            sc = librosa.feature.spectral_centroid(y=y, sr=sr)[0]

            # Zero Crossing Rate (ZCR) — "percussiveness" of the sound.
            # Shows how often the sound wave crosses zero
            # High ZCR = "noisy", "harsh" sound (e.g., hi-hat, noise)
            # Low ZCR = "smooth", "clean" sound (e.g., sine wave)
            # Value from 0 to 1
            zcr = librosa.feature.zero_crossing_rate(y)[0]

        except Exception as e:
            # If something went wrong — show a user-friendly message
            # The previously loaded track (if any) stays available for plotting
            showerror(title='Error', message=f'Failed to load file:\n{str(e)}')
            return None

        # Everything succeeded — only now update the stored state
        self.path_mp3 = path
        self.y, self.sr = y, sr
        self.duration = duration
        self.tempo = tempo
        self.key = key
        self.rms = rms
        self.sc = sc
        self.zcr = zcr

        # Output to label
        report = {
            "path": self.path_mp3,
            "duration": round(self.duration, 1),
            "tempo": int(self.tempo[0]),
            "key": self.key,
            "sample_rate": self.sr
        }

        return report

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