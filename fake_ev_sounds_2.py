import time
import obd
from obd import OBDCommand
from obd.protocols import ECU
from obd.decoders import noop
import pygame
import numpy as np
import random 


pygame.mixer.pre_init(44100, -16, 2, 128)
pygame.init()
pygame.mixer.init(buffer=128)
pygame.mixer.set_num_channels(128)

CYLINDER_FILE = "engine_loop.mp3"

BURBLE_FILES = [
    "burble_one.mp3",
    "burble_short.mp3",
    "burble_medium.mp3",
    "burble_long.mp3",
    "burble_really_long.mp3",
    "burble_shift.mp3",
]

base_sound = pygame.mixer.Sound(CYLINDER_FILE)
base_array = pygame.sndarray.array(base_sound)


burble_sounds = [pygame.mixer.Sound(f) for f in BURBLE_FILES]
for s in burble_sounds:
    s.set_volume(1.0)

def make_pitch_sound(array, pitch):
    length = max(1, int(len(array) / pitch))
    old_idx = np.arange(len(array))
    new_idx = np.linspace(0, len(array) - 1, length)

    if array.ndim == 2:
        left = np.interp(new_idx, old_idx, array[:, 0])
        right = np.interp(new_idx, old_idx, array[:, 1])
        pitched = np.column_stack((left, right))
    else:
        pitched = np.interp(new_idx, old_idx, array)

    return pygame.sndarray.make_sound(pitched.astype(array.dtype))


RAW_220101 = OBDCommand(
    "RAW_220101",
    "Raw BMS 220101",
    b"220101",
    70,
    noop,
    ECU.ALL,
    False,
    header=b"7E4"
)

def signed_byte(x):
    return x - 256 if x >= 128 else x

def signed_16(high, low):
    raw = (high << 8) + low
    return raw - 65536 if raw >= 32768 else raw

def decode_battery(data):
    # remove 62 01 01 response header
    d = data[3:]

    # Torque letters:
    # K = d[10], L = d[11]
    # M = d[12], N = d[13]
    amps = signed_16(d[10], d[11]) / 10
    volts = ((d[12] << 8) + d[13]) / 10
    kw = amps * volts / 1000

    return amps, volts, kw

connection = obd.OBD("COM8", fast=False, timeout=2)

print("Connected:", connection.is_connected())
print("Status:", connection.status())
last_kw = 0
last_pitch_step = 0
try:
    while True:
        r = connection.query(RAW_220101, force=True)

        if r.is_null():
            print("NO DATA")
            time.sleep(0.2)
            continue

        amps, volts, kw = decode_battery(r.value)

        print(
            f"\rBattery: {volts:.1f} V | {amps:.1f} A | {kw:.1f} kW",
            end="",
            flush=True
        )
        pitch = kw / 10
        pitch = max(3, pitch)
        pitch_step = round(pitch * 10) / 10

        if pitch_step != last_pitch_step:
            pitched_sound = make_pitch_sound(base_array, pitch_step)
            pitched_sound.set_volume(0.10)
            last_pitch_step = pitch_step
        if ((last_kw - kw) > 40) and kw >= 0:
            burble = random.choice(burble_sounds)
            ch = pygame.mixer.find_channel()
            if ch:
                ch.play(burble)
                print(" BURBLE")
        

        last_kw = kw
        time.sleep(0.05)
except KeyboardInterrupt:
    pass

connection.close()