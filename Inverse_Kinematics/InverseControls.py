'''
Code provided by Professor Ngo
Edited by Ethan Matthews
'''

import tkinter as tk
from tkinter import scrolledtext
import threading
import serial
import time

# ------------------------
# SERIAL SETUP
# ------------------------
SERIAL_PORT = "/dev/ttyACM0"   # Change this if needed
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
root.title("XYZ Robotic Arm Controller")
root.geometry("600x500")

x_val = 4
y_val = 4
z_val = 4


# ------------------------
# FUNCTIONS
# ------------------------
def send_to_arduino(cmd):
    if arduino:
        arduino.write((cmd + "\n").encode())
        log(f"SENT → {cmd}")


def log(msg):
    text_box.insert(tk.END, msg + "\n")
    text_box.see(tk.END)


def send_xyz():
    cmd = f"{x_val} {y_val} {z_val}"
    send_to_arduino(cmd)


def update_x(val):
    global x_val
    x_val = int(val)
    send_xyz()


def update_y(val):
    global y_val
    y_val = int(val)
    send_xyz()


def update_z(val):
    global z_val
    z_val = int(val)
    send_xyz()


def read_serial():
    while True:
        if arduino:
            try:
                line = arduino.readline().decode().strip()
                if line:
                    log(f"ARDUINO → {line}")
            except Exception as e:
                log(f"Serial error: {e}")
        time.sleep(0.05)


def reset_xyz():
    slider_x.set(4)
    slider_y.set(4)
    slider_z.set(4)


# ------------------------
# GUI LAYOUT
# ------------------------
slider_frame = tk.Frame(root)
slider_frame.pack(pady=20)

# ----- X slider -----
x_frame = tk.Frame(slider_frame)
x_frame.grid(row=0, column=0, padx=20)

slider_x = tk.Scale(
    x_frame, from_=8, to=0, orient=tk.VERTICAL,
    label="X", length=250, command=update_x
)
slider_x.set(4)
slider_x.pack()

# ----- Y slider -----
y_frame = tk.Frame(slider_frame)
y_frame.grid(row=0, column=1, padx=20)

slider_y = tk.Scale(
    y_frame, from_=8, to=0, orient=tk.VERTICAL,
    label="Y", length=250, command=update_y
)
slider_y.set(4)
slider_y.pack()

# ----- Z slider -----
z_frame = tk.Frame(slider_frame)
z_frame.grid(row=0, column=2, padx=20)

slider_z = tk.Scale(
    z_frame, from_=8, to=0, orient=tk.VERTICAL,
    label="Z", length=250, command=update_z
)
slider_z.set(4)
slider_z.pack()

# Reset button
tk.Button(root, text="RESET (X=Y=Z=0)", command=reset_xyz,
          height=2, bg="#f0d060").pack(pady=10)

# Serial log viewer
text_box = scrolledtext.ScrolledText(root, width=70, height=12)
text_box.pack(pady=10)

# Start serial read thread
threading.Thread(target=read_serial, daemon=True).start()

# Run GUI
root.mainloop()
