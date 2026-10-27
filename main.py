#main.py
# import GUI module
import tkinter as tk

# import module for running the library preloading in the background
import threading

# import my module where all button functions are defined
import analyzer

# initialize the main window
window = tk.Tk()
# set window size
window.geometry('680x540')
# set window title
window.title('Music Analyzer')
# set resizability, yes/no
window.resizable(width=False, height=False)

# label
main_label = tk.Label(background='white', borderwidth=8, height=22, font=12,
                      justify=tk.LEFT, wraplength=600)
# place the text label
main_label.grid(row=1, column=0, columnspan=6,
                padx=15,
                sticky=tk.EW)

# create a MusicAnalyzer class object that already has all functions and necessary attributes
music_analyzer = analyzer.MusicAnalyzer()

def handle_load():
    # remember the current text, so it can be restored if loading is cancelled or fails
    previous_text = main_label['text']

    main_label['text'] = 'Loading...'
    main_label.update()

    data = music_analyzer.load_mp3()
    if data:
        main_label['text'] = (
            f"Path: {data['path']}\n\n"
            f"Duration: {data['duration']} sec\n"
            f"Tempo: {data['tempo']} BPM\n"
            f"Key: {data['key']}\n"
            f"Sample Rate: {data['sample_rate']} Hz\n"
        )
    else:
        # cancelled or failed (the error window was already shown):
        # the analyzer data is unchanged, so show the previous result again
        main_label['text'] = previous_text


# buttons
# command=music_analyzer.load_mp3 - reference to the music_analyzer class method that loads, collects, and analyzes all data
load_mp3_button = tk.Button(text='Load MP3', font=16, command=handle_load)
load_mp3_button.grid(row=0, column=0, columnspan=3,
                     ipadx=50, ipady=20, padx=70, pady=20,
                     sticky=tk.NW)

analyze_button = tk.Button(text='Analyze', font=16, command=music_analyzer.analyze)
analyze_button.grid(row=0, column=3, columnspan=3,
                     ipadx=50, ipady=20, padx=70, pady=20,
                    sticky=tk.NW)

# --- background preloading of heavy libraries (librosa, matplotlib) ---
# buttons are disabled until the libraries are ready, so the window appears instantly
load_mp3_button.config(state='disabled')
analyze_button.config(state='disabled')
main_label['text'] = 'Loading libraries...'

# event that the background thread sets when it is done
libs_ready = threading.Event()
# stores an import error (if any), to show it in the main thread
libs_error = []

def preload():
    # runs in a background thread: must NOT touch any Tkinter widgets
    try:
        analyzer.preload_libs()
    except Exception as e:
        libs_error.append(e)
    libs_ready.set()

def check_ready():
    # runs in the main thread: polls the event every 100 ms
    if not libs_ready.is_set():
        window.after(100, check_ready)
    elif libs_error:
        main_label['text'] = f'Failed to load libraries:\n{libs_error[0]}'
    else:
        load_mp3_button.config(state='normal')
        analyze_button.config(state='normal')
        main_label['text'] = ''

# run the window
if __name__ == "__main__":
    threading.Thread(target=preload, daemon=True).start()
    window.after(100, check_ready)
    window.mainloop()