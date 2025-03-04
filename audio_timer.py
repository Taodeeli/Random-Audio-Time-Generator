import pygame.mixer
import threading
import random
import time
import os
import tkinter as tk
from tkinter import filedialog, scrolledtext
import pystray
from pystray import MenuItem as item
from PIL import Image, ImageDraw

# Initialize Pygame mixer
pygame.mixer.init()
timer_threads = []
tray_icon = None  # System tray icon reference

def play_sound(file_path):
    """Plays the given MP3 file for a random duration between 3-10 seconds."""
    pygame.mixer.music.load(file_path)
    pygame.mixer.music.play()
    duration = random.randint(3, 10)
    time.sleep(duration)
    pygame.mixer.music.stop()

def start_random_timers():
    """Stops previous timers and schedules new random timers."""
    stop_timers()  # Stop any existing timers before starting new ones
    
    try:
        min_time = int(min_time_min_entry.get()) * 60 + int(min_time_sec_entry.get())
        max_time = int(max_time_min_entry.get()) * 60 + int(max_time_sec_entry.get())
        num_sounds = int(num_sounds_entry.get())
        
        if not audio_files:
            log_output.insert(tk.END, "No audio files selected!\n")
            log_output.see(tk.END)
            return
        
        def schedule_sounds():
            for _ in range(num_sounds):
                delay = random.randint(min_time, max_time)
                sound_file = random.choice(audio_files)
                timer = threading.Timer(delay, play_sound, args=(sound_file,))
                timer.start()
                timer_threads.append(timer)
                log_output.insert(tk.END, f"Scheduled {sound_file} to play in {delay // 60} min {delay % 60} sec.\n")
                log_output.see(tk.END)
            
            if loop_var.get():
                timer = threading.Timer(max_time, schedule_sounds)
                timer.start()
                timer_threads.append(timer)

        schedule_sounds()

    except ValueError:
        log_output.insert(tk.END, "Invalid input! Please enter valid numbers.\n")
        log_output.see(tk.END)

def stop_timers():
    """Stops all active timers and any playing audio."""
    for timer in timer_threads:
        timer.cancel()
    timer_threads.clear()
    pygame.mixer.music.stop()
    log_output.insert(tk.END, "All timers and audio have been stopped.\n")
    log_output.see(tk.END)

def load_files_from_folder():
    """Loads MP3 files from a selected folder."""
    folder = filedialog.askdirectory()
    if folder:
        audio_files.clear()
        for file in os.listdir(folder):
            if file.endswith(".mp3"):
                audio_files.append(os.path.join(folder, file))
        log_output.insert(tk.END, "Loaded files:\n" + "\n".join(audio_files) + "\n")
        log_output.see(tk.END)

def create_tray_icon():
    """Creates a system tray icon with menu options."""
    global tray_icon

    def restore_window(icon, item):
        """Restores the window from the system tray."""
        root.after(0, root.deiconify)
        tray_icon.stop()  # Stop the tray icon

    def exit_application(icon, item):
        """Stops the application and exits."""
        stop_timers()
        tray_icon.stop()
        root.quit()

    # Create an icon image
    image = Image.new('RGB', (64, 64), (255, 255, 255))
    draw = ImageDraw.Draw(image)
    draw.rectangle([16, 16, 48, 48], fill=(0, 0, 0))

    menu = (item('Show', restore_window), item('Exit', exit_application))
    tray_icon = pystray.Icon("audio_timer", image, "Audio Timer", menu)
    tray_icon.run()

def on_close():
    """Minimizes the app to the system tray when closed."""
    root.withdraw()  # Hide the main window
    threading.Thread(target=create_tray_icon, daemon=True).start()  # Run tray in background

# GUI Setup
root = tk.Tk()
root.title("Random Audio Timer")
root.protocol("WM_DELETE_WINDOW", on_close)  # Override close button

audio_files = []

# Min Time Input
tk.Label(root, text="Min Time (minutes & seconds):").pack()
min_time_frame = tk.Frame(root)
min_time_frame.pack()
min_time_min_entry = tk.Entry(min_time_frame, width=5)
min_time_min_entry.pack(side=tk.LEFT)
min_time_min_entry.insert(0, "1")
tk.Label(min_time_frame, text="min").pack(side=tk.LEFT)
min_time_sec_entry = tk.Entry(min_time_frame, width=5)
min_time_sec_entry.pack(side=tk.LEFT)
min_time_sec_entry.insert(0, "0")
tk.Label(min_time_frame, text="sec").pack(side=tk.LEFT)

# Max Time Input
tk.Label(root, text="Max Time (minutes & seconds):").pack()
max_time_frame = tk.Frame(root)
max_time_frame.pack()
max_time_min_entry = tk.Entry(max_time_frame, width=5)
max_time_min_entry.pack(side=tk.LEFT)
max_time_min_entry.insert(0, "5")
tk.Label(max_time_frame, text="min").pack(side=tk.LEFT)
max_time_sec_entry = tk.Entry(max_time_frame, width=5)
max_time_sec_entry.pack(side=tk.LEFT)
max_time_sec_entry.insert(0, "0")
tk.Label(max_time_frame, text="sec").pack(side=tk.LEFT)

# Number of Sounds Input
tk.Label(root, text="Number of Sounds:").pack()
num_sounds_entry = tk.Entry(root)
num_sounds_entry.pack()
num_sounds_entry.insert(0, "5")

# Loop Checkbox
loop_var = tk.BooleanVar()
tk.Checkbutton(root, text="Loop Timer", variable=loop_var).pack()

# Buttons
tk.Button(root, text="Select Folder", command=load_files_from_folder).pack()
tk.Button(root, text="Start Timer", command=start_random_timers).pack()
tk.Button(root, text="Stop Timer", command=stop_timers).pack()

# Log Output Box
log_output = scrolledtext.ScrolledText(root, width=60, height=10, wrap=tk.WORD)
log_output.pack()

root.mainloop()
