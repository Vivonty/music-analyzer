#main.py
# import GUI module
import tkinter as tk

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
        main_label['text'] = 'File loading error or cancelled'


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

# run the window
if __name__ == "__main__":
    window.mainloop()