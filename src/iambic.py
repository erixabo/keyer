#!/usr/bin/env python3
# Stabil iambic keyer egérrel – BAL=DIT, JOBB=DAH
# Ctrl+C kilépés

import time
import numpy as np
import sounddevice as sd
from evdev import InputDevice, ecodes

MOUSE_EVENT = "/dev/input/event3"   # a te egered

# --- CW paraméterek ---
wpm = 20
sidetone_hz = 600
sample_rate = 48000

def dit_ms(w): return 1200.0/float(w)
T_dit_ms = dit_ms(wpm)
unit = T_dit_ms/1000.0

# Állapot
dit_pressed = False
dah_pressed = False
last_iambic = 1

# Audio
phase=0.0; amp=0.0; target=0.0
ramp_step = 1.0/(sample_rate*0.003)

def audio_callback(outdata, frames, time_info, status):
    global phase, amp, target
    phase_inc = 2*np.pi*sidetone_hz/sample_rate
    t = np.arange(frames, dtype=np.float32)
    arr = np.empty(frames, dtype=np.float32)
    a = amp
    for i in range(frames):
        if target>a: a=min(target,a+ramp_step)
        elif target<a: a=max(target,a-ramp_step)
        arr[i]=a
    amp=a
    sig = np.sin(phase+phase_inc*t)*arr
    phase=float((phase+phase_inc*frames)%(2*np.pi))
    outdata[:] = sig.reshape(-1,1)

stream = sd.OutputStream(channels=1,samplerate=sample_rate,callback=audio_callback)
stream.start()

print("Egér-keyer indul: BAL=DIT, JOBB=DAH, együtt=iambic | Ctrl+C kilépés")

dev = InputDevice(MOUSE_EVENT)
dev.grab()

state=0
t_end=time.time()

try:
    while True:
        # --- Olvass egy eseményt, ha van ---
        event = dev.read_one()
        if event and event.type == ecodes.EV_KEY:
            if event.code == ecodes.BTN_LEFT:
                dit_pressed = (event.value==1)
            elif event.code == ecodes.BTN_RIGHT:
                dah_pressed = (event.value==1)

        now=time.time()

        if state==0:  # IDLE
            #if dit_pressed and dah_pressed:
             #   last_iambic=1-last_iambic
                #elem='dit' if last_iambic==0 else 'dah'
            if dit_pressed: elem='dit'
            elif dah_pressed: elem='dah'
            else: elem=None

            if elem:
                if elem=='dit': target=1.0; t_end=now+unit; state=1
                else: target=1.0; t_end=now+3*unit; state=2

        elif state in (1,2):  # DIT/DAH jel
            if now>=t_end:
                target=0.0
                t_end=now+unit
                state=3

        elif state==3:  # szünet
            if now>=t_end: state=0

        time.sleep(0.001)

except KeyboardInterrupt:
    pass
finally:
    dev.ungrab()
    stream.stop(); stream.close()
    print("\nKilépés.")
