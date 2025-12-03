'''
Code provided by Professor Ngo
'''

import tkinter as tk
from tkinter import filedialog, scrolledtext
import threading
import serial
import time

# ------------------------
# SERIAL SETUP
# ------------------------
SERIAL_PORT = "/dev/ttyACM0"   # ← Change for your computer
BAUD_RATE = 9600

try:
    arduino = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
    time.sleep(2)
    print("Connected to Arduino")
except:
    arduino = None
    print("Could not connect to Arduino")


# ------------------------
# GUI + GLOBAL STATE
# ------------------------
root = tk.Tk()
root.title("6-DOF Robotic Arm Controller — Interactive + Script Mode")
root.geometry("800x600")

sliders = []
values = [90] * 6
command_list = []
command_index = 0
running_sequence = False


# ------------------------
# FUNCTIONS
# ------------------------
def send_to_arduino(cmd):
    """Send a line to Arduino."""
    if arduino:
        arduino.write((cmd + "\n").encode())
        log(f"SENT → {cmd}")


def log(msg):
    """Append text to log window."""
    text_box.insert(tk.END, msg + "\n")
    text_box.see(tk.END)


def update_servo(idx, val):
    """Send servo positions when slider is released."""
    values[idx] = int(val)
    cmd = " ".join(str(v) for v in values)
    send_to_arduino(cmd)


def adjust_servo(idx, delta):
    """Up/Down buttons — change value & send immediately."""
    v = sliders[idx].get()
    v = max(0, min(180, v + delta))
    sliders[idx].set(v)
    values[idx] = v
    cmd = " ".join(str(x) for x in values)
    send_to_arduino(cmd)


def read_serial():
    """Thread: continuously read Arduino responses."""
    global running_sequence, command_index

    while True:
        if arduino:
            try:
                line = arduino.readline().decode().strip()
                if line:
                    log(f"ARDUINO → {line}")

                    # If running sequence and Arduino replies "OK", send next command
                    if running_sequence and line.upper() == "OK":
                        send_next_sequence_command()

            except Exception as e:
                log(f"Serial error: {e}")
        time.sleep(0.05)


def load_command_file():
    """Load a file containing servo commands."""
    global command_list, command_index

    filepath = filedialog.askopenfilename(
        title="Select Command File",
        filetypes=[("Text Files", "*.txt")]
    )
    if not filepath:
        return

    with open(filepath, "r") as f:
        lines = f.read().strip().splitlines()

    # Keep only valid lines (6 integers)
    command_list = []
    for line in lines:
        parts = line.strip().split()
        if len(parts) == 6 and all(p.isdigit() for p in parts):
            command_list.append(line)

    command_index = 0
    log(f"Loaded {len(command_list)} commands.")
    if len(command_list) == 0:
        log("WARNING: No valid commands found.")


def send_next_sequence_command():
    """Send next line in the loaded script."""
    global command_index, running_sequence

    if command_index >= len(command_list):
        log("Sequence complete.")
        running_sequence = False
        return

    cmd = command_list[command_index]
    send_to_arduino(cmd)
    command_index += 1


def start_sequence():
    """User clicks Run Sequence."""
    global running_sequence, command_index

    if not command_list:
        log("No file loaded.")
        return

    if running_sequence:
        log("Sequence already running.")
        return

    command_index = 0
    running_sequence = True
    log("Starting sequence…")

    send_next_sequence_command()


def reset_servos():
    """Move all servos to center position (90°)."""
    for i in range(6):
        sliders[i].set(90)
        values[i] = 90

    cmd = " ".join("90" for _ in range(6))
    send_to_arduino(cmd)


# ------------------------
# GUI LAYOUT
# ------------------------
servo_frame = tk.Frame(root)
servo_frame.pack(pady=15)

for i in range(6):
    col = tk.Frame(servo_frame)
    col.grid(row=0, column=i, padx=10)
    slider = tk.Scale(col, from_=180, to=0, length=220,
                      label=f"Servo {i+1}", orient=tk.VERTICAL)
    slider.set(90)
    slider.pack()
    sliders.append(slider)

    # Bind: send command only when slider released
    slider.bind("<ButtonRelease-1>",
                lambda e, idx=i: update_servo(idx, sliders[idx].get()))

    tk.Button(col, text="▲", command=lambda idx=i: adjust_servo(idx, +1)).pack(fill="x", pady=2)
    tk.Button(col, text="▼", command=lambda idx=i: adjust_servo(idx, -1)).pack(fill="x")


# Reset button
tk.Button(root, text="RESET (All 90°)", command=reset_servos,
          height=2, bg="#f0d060").pack(pady=10)


# File loader + sequence controller
file_frame = tk.Frame(root)
file_frame.pack(pady=10)

tk.Button(file_frame, text="Load Command File", command=load_command_file).grid(row=0, column=0, padx=10)
tk.Button(file_frame, text="Run Sequence", command=start_sequence).grid(row=0, column=1, padx=10)


# Serial log viewer
text_box = scrolledtext.ScrolledText(root, width=90, height=15)
text_box.pack(pady=10)


# Start serial reading thread
threading.Thread(target=read_serial, daemon=True).start()


# Run GUI
root.mainloop()