# Music Analyzer

A simple desktop application for musical and physical audio analysis. It extracts track characteristics and visualizes them using charts.

## Features
* **Key Detection:** Uses Krumhansl-Schmuckler algorithm via Pearson correlation to determine the musical key.
* **Tempo Extraction:** Detects track BPM (Beats Per Minute).
* **Audio Visualizations:** Plots single-window charts for:
  * RMS (Loudness)
  * Spectral Centroid (Brightness)
  * Zero Crossing Rate (Percussiveness)

## Technologies Used
* Python 3
* Tkinter (GUI)
* Librosa (Audio Analysis)
* Matplotlib (Plotting)
* NumPy (Matrix Operations)

## How to Run

1. Clone the repository or download the source code.
2. Install required dependencies:
   ```bash
   pip install librosa matplotlib numpy
   
Run the application:

```bash
    python main.py