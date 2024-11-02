import pyaudio
import numpy as np
import tkinter as tk
from tkinter import font
from tkinter import ttk
import time

# Initialize Tkinter window
root = tk.Tk()
root.title("Real-Time Decibel and Calorie Monitor")

# Window size and background color
root.geometry("500x400")
root.configure(bg="#F0F8FF")  # Light blue background

# Add custom fonts
label_font = font.Font(family="Helvetica", size=14, weight="bold")
calorie_font = font.Font(family="Helvetica", size=18, weight="bold")

# Labels to display decibel level and calories
decibel_label = tk.Label(root, text="Decibel Level: 0 dB", font=label_font, bg="#F0F8FF", fg="#2E8B57")
calories_label = tk.Label(root, text="Calories Burnt: 0.00 calories", font=calorie_font, bg="#F0F8FF", fg="#FF6347")
decibel_label.pack(pady=20)
calories_label.pack(pady=10)

# Progress bars
decibel_progress = ttk.Progressbar(root, length=300, mode="determinate", maximum=100)
decibel_progress.pack(pady=10)

calories_progress = ttk.Progressbar(root, length=300, mode="determinate", maximum=100)
calories_progress.pack(pady=10)

# Variables to store current state
calories = 0.0
last_decibel_time = time.time()  # Track the last time we had significant sound
silence_threshold = 20  # dB level considered as silence
silence_duration = 5  # Time in seconds to wait before stopping calorie increase

# Function to calculate decibels from audio
def calculate_decibel(data):
    rms = np.sqrt(np.mean(np.square(data)))
    if rms == 0:
        return 0  # Return 0 dB if there's complete silence
    decibels = 20 * np.log10(rms)
    return decibels
# Function to update calories based on decibels
def update_calories(decibels):
    global calories, last_decibel_time
    # If decibels exceed a threshold (e.g., 30 dB), increase calories
    if decibels > 30:
        calories += (decibels - 30) * 0.1  # Arbitrary formula for calories
        last_decibel_time = time.time()  # Reset the timer when there's sound

    # If silence (decibels below threshold) persists for too long, stop increasing calories
    elif time.time() - last_decibel_time > silence_duration:
        pass  # Calories stop increasing but do not reset

# Function to reset values
def reset_values():
    global calories
    calories = 0.0  # Reset calories to 0
    decibel_progress["value"] = 0  # Reset decibel progress bar to 0
    calories_progress["value"] = 0  # Reset calorie progress bar to 0
    decibel_label.config(text="Decibel Level: 0 dB")  # Reset decibel label
    calories_label.config(text="Calories Burnt: 0.00 calories")  # Reset calorie label

# Adding the Reset Button to the GUI
reset_button = tk.Button(
    root,
    text="Reset",
    command=reset_values,  # Link the reset_values function to this button
    font=("Helvetica", 12),
    bg="#FFD700",  # Golden background color
    fg="#FFFFFF",  # White text color
    relief="raised",  # Raised button effect
    padx=20, pady=10  # Padding inside the button
)
reset_button.pack(pady=20)  # Pack the button with some vertical padding

# Initialize PyAudio
p = pyaudio.PyAudio()

# Function to capture audio and update UI
def capture_audio():
    global calories
    # Capture audio stream
    stream = p.open(format=pyaudio.paInt16,
                    channels=1,
                    rate=44100,
                    input=True,
                    frames_per_buffer=1024)

    data = np.frombuffer(stream.read(1024), dtype=np.int16)
    decibels = calculate_decibel(data)

    # Update calories based on decibels
    update_calories(decibels)

    # Update the Tkinter labels with dynamic text color based on decibels
    decibel_label.config(text=f"Decibel Level: {decibels:.2f} dB", fg="#2E8B57" if decibels > 30 else "#DC143C")
    calories_label.config(text=f"Calories Burnt: {calories:.2f} calories", fg="#FF6347")

    # Update the progress bars
    decibel_progress["value"] = min(decibels, 100)
    calories_progress["value"] = min(calories, 100)

    # Repeat every 100ms
    root.after(100, capture_audio)

# Start capturing audio
capture_audio()

# Run the Tkinter event loop
root.mainloop()