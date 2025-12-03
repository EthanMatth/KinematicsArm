'''
ForwardControl GUI - Fixed sliders + clean shutdown
Edited by Ethan Matthews (fixed)
'''

import tkinter as tk
from tkinter import filedialog, scrolledtext
import threading
import serial
import time

# ------------------------
# SERIAL SETUP
# ------------------------
SERIAL_PORT = "/dev/ttyACM1"   # Change this if needed
BAUD_RATE = 9600

try:
    arduino = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
    time.sleep(2)
    print("Connected to Arduino")
except Exception as e:
    arduino = None
    print("Could not connect to Arduino:", e)


# ------------------------
# GUI + GLOBAL STATE
# ------------------------
root = tk.Tk()
root.title("XYZ + Angles Robotic Arm Controller")
root.geometry("900x650")
running_sequence = False

# XYZ coordinates (0..8)
x_val = 0
y_val = 0
z_val = 8

# Orientation angles (0..180)
alpha_val = 90
beta_val = 90
gamma_val = 90

# Claw state (0 closed, 1 open)
claw_state = 1

# Thread control
stop_event = threading.Event()


# ------------------------
# FUNCTIONS
# ------------------------
def send_to_arduino(cmd):
    if arduino:
        try:
            arduino.write((cmd + "\n").encode())
            log(f"SENT → {cmd}")
        except Exception as e:
            log(f"Serial write error: {e}")

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
        if len(parts) == 7 and all(p.isdigit() for p in parts):
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


def log(msg):
    text_box.insert(tk.END, msg + "\n")
    text_box.see(tk.END)


def send_all():
    """Send full command: x y z alpha beta gamma claw"""
    cmd = f"{x_val} {y_val} {z_val} {alpha_val} {beta_val} {gamma_val} {claw_state}"
    send_to_arduino(cmd)


def update_x(val):
    global x_val
    x_val = int(val)
    send_all()


def update_y(val):
    global y_val
    y_val = int(val)
    send_all()


def update_z(val):
    global z_val
    z_val = int(val)
    send_all()


def update_alpha(val):
    global alpha_val
    alpha_val = int(val)
    send_all()


def update_beta(val):
    global beta_val
    beta_val = int(val)
    send_all()


def update_gamma(val):
    global gamma_val
    gamma_val = int(val)
    send_all()


def open_claw():
    global claw_state
    claw_state = 1
    send_all()


def close_claw():
    global claw_state
    claw_state = 0
    send_all()


def read_serial():
    """Background serial reader that stops when stop_event is set."""
    while not stop_event.is_set():
        if arduino:
            try:
                line = arduino.readline().decode(errors="ignore").strip()
                if line:
                    log(f"ARDUINO → {line}")

                    if running_sequence and line.upper() == "OK":
                        send_next_sequence_command()
            except Exception as e:
                log(f"Serial read error: {e}")
        # small sleep to avoid busy loop
        time.sleep(0.05)


def reset_all():
    slider_x.set(0)
    slider_y.set(0)
    slider_z.set(8)
    slider_alpha.set(90)
    slider_beta.set(90)
    slider_gamma.set(90)
    close_claw()


def on_closing():
    """Clean shutdown: stop thread, close serial, then destroy window."""
    log("Shutting down...")
    stop_event.set()
    # give reader thread a small moment to finish
    time.sleep(0.1)
    try:
        if arduino and arduino.is_open:
            arduino.close()
            log("Closed serial port.")
    except Exception as e:
        log(f"Error closing serial: {e}")
    root.destroy()


# ------------------------
# GUI LAYOUT
# ------------------------
main_frame = tk.Frame(root)
main_frame.pack(pady=10, fill="both", expand=True)

# Top: sliders
sliders_frame = tk.Frame(main_frame)
sliders_frame.pack(pady=10)

# XYZ group
xyz_group = tk.LabelFrame(sliders_frame, text="Position (X, Y, Z)", padx=10, pady=10)
xyz_group.grid(row=0, column=0, padx=15)

slider_x = tk.Scale(xyz_group, from_=8, to=-8, orient=tk.VERTICAL,
                    label="X", length=260, command=update_x)
slider_x.bind("<ButtonRelease-1>", lambda e: update_x(slider_x.get()))
slider_x.set(x_val)
slider_x.grid(row=0, column=0, padx=8)

slider_y = tk.Scale(xyz_group, from_=8, to=0, orient=tk.VERTICAL,
                    label="Y", length=260, command=update_y)
slider_y.bind("<ButtonRelease-1>", lambda e: update_y(slider_y.get()))
slider_y.set(y_val)
slider_y.grid(row=0, column=1, padx=8)

slider_z = tk.Scale(xyz_group, from_=8, to=0, orient=tk.VERTICAL,
                    label="Z", length=260, command=update_z)
slider_z.bind("<ButtonRelease-1>", lambda e: update_z(slider_z.get()))
slider_z.set(z_val)
slider_z.grid(row=0, column=2, padx=8)

# Angles group
angle_group = tk.LabelFrame(sliders_frame, text="Orientation Angles (α, β, γ)", padx=10, pady=10)
angle_group.grid(row=0, column=1, padx=15)

slider_alpha = tk.Scale(angle_group, from_=180, to=0, orient=tk.VERTICAL,
                        label="Alpha (°)", length=260, command=update_alpha)
slider_alpha.bind("<ButtonRelease-1>", lambda e: update_alpha(slider_alpha.get()))
slider_alpha.set(alpha_val)
slider_alpha.grid(row=0, column=0, padx=8)

slider_beta = tk.Scale(angle_group, from_=180, to=0, orient=tk.VERTICAL,
                       label="Beta (°)", length=260, command=update_beta)
slider_beta.bind("<ButtonRelease-1>", lambda e: update_beta(slider_beta.get()))
slider_beta.set(beta_val)
slider_beta.grid(row=0, column=1, padx=8)

slider_gamma = tk.Scale(angle_group, from_=180, to=0, orient=tk.VERTICAL,
                        label="Gamma (°)", length=260, command=update_gamma)
slider_gamma.bind("<ButtonRelease-1>", lambda e: update_gamma(slider_gamma.get()))
slider_gamma.set(gamma_val)
slider_gamma.grid(row=0, column=2, padx=8)

# Claw controls and reset
controls_frame = tk.Frame(main_frame)
controls_frame.pack(pady=12)

claw_frame = tk.LabelFrame(controls_frame, text="Claw Control", padx=10, pady=10)
claw_frame.grid(row=0, column=0, padx=10)

btn_open = tk.Button(claw_frame, text="OPEN CLAW", width=14, bg="#a0f0a0", command=open_claw)
btn_open.grid(row=0, column=0, padx=8, pady=6)

btn_close = tk.Button(claw_frame, text="CLOSE CLAW", width=14, bg="#f0a0a0", command=close_claw)
btn_close.grid(row=0, column=1, padx=8, pady=6)

reset_btn = tk.Button(controls_frame, text="RESET ALL", command=reset_all, height=2, bg="#f0d060")
reset_btn.grid(row=0, column=1, padx=20)

# File loader + sequence controller
file_frame = tk.Frame(root)
file_frame.pack(pady=10)

tk.Button(file_frame, text="Load Command File", command=load_command_file).grid(row=0, column=0, padx=10)
tk.Button(file_frame, text="Run Sequence", command=start_sequence).grid(row=0, column=1, padx=10)

# Serial log viewer
text_box = scrolledtext.ScrolledText(root, width=110, height=14)
text_box.pack(pady=10)

# Start serial read thread
reader_thread = threading.Thread(target=read_serial, daemon=True)
reader_thread.start()

# Bind window close
root.protocol("WM_DELETE_WINDOW", on_closing)

# Run GUI
root.mainloop()
