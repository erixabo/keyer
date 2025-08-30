#!/usr/bin/env python3
# Iambic A keyer – → = DIT sorozat, ↓ = DAH sorozat, együtt = iambic
# Q = kilépés

import time
import numpy as np
import sounddevice as sd
from pynput import keyboard

# --- Beállítások ---
wpm = 20
sidetone_hz = 600
sample_rate = 48000

def dit_ms(w):
    return 1200.0 / float(w)  # PARIS standard

T_dit_ms = dit_ms(wpm)
unit = T_dit_ms / 1000.0

# gombállapotok
dit_pressed = False
dah_pressed = False
running = True
last_iambic = 1  # váltogatáshoz

# audio állapot
phase = 0.0
amp = 0.0
target = 0.0
ramp_step = 1.0 / (sample_rate * 0.003)

def audio_callback(outdata, frames, time_info, status):
    global phase, amp, target
    phase_inc = 2*np.pi*sidetone_hz/sample_rate
    t = np.arange(frames, dtype=np.float32)
    # rámpa
    a = amp
    arr = np.empty(frames, dtype=np.float32)
    for i in range(frames):
        if target > a:
            a = min(target, a+ramp_step)
        elif target < a:
            a = max(target, a-ramp_step)
        arr[i] = a
    amp = a
    sig = np.sin(phase + phase_inc*t) * arr
    phase = float((phase + phase_inc*frames) % (2*np.pi))
    outdata[:] = sig.reshape(-1,1)

stream = sd.OutputStream(channels=1, samplerate=sample_rate, callback=audio_callback)
stream.start()

# billentyű
def on_press(key):
    global dit_pressed, dah_pressed, running
    try:
        if key == keyboard.Key.right: dit_pressed = True
        elif key == keyboard.Key.down: dah_pressed = True
        elif key.char in ('q','Q'): running=False
    except: pass

def on_release(key):
    global dit_pressed, dah_pressed
    if key == keyboard.Key.right: dit_pressed = False
    elif key == keyboard.Key.down: dah_pressed = False

listener = keyboard.Listener(on_press=on_press, on_release=on_release)
listener.start()

print("Iambic keyer: → DAH, ↓ DIT, együtt iambic | Q kilépés")

state = 0
t_end = time.time()

while running:
    now = time.time()
    if state == 0:  # IDLE
        # ha valamelyik gomb nyomva van, ütemet indítunk
        if dit_pressed and dah_pressed:
            last_iambic = 1 - last_iambic
            elem = 'dit' if last_iambic==0 else 'dah'
        elif dit_pressed:
            elem = 'dit'
        elif dah_pressed:
            elem = 'dah'
        else:
            elem = None

        if elem:
            if elem == 'dit':
                target=1.0
                t_end=now+unit
                state=1
            elif elem == 'dah':
                target=1.0
                t_end=now+3*unit
                state=2

    elif state == 1:  # DIT jel
        if now >= t_end:
            target=0.0
            t_end=now+unit  # 1 dit szünet
            state=3

    elif state == 2:  # DAH jel
        if now >= t_end:
            target=0.0
            t_end=now+unit
            state=3

    elif state == 3:  # szünet
        if now >= t_end:
            state=0  # vissza IDLE-be

    time.sleep(0.001)

listener.stop()
stream.stop()
stream.close()
print("Kilépés.")
