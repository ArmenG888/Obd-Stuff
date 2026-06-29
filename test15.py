import time
import random
import pygame
import numpy as np

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

RPM_MIN = 900
RPM_MAX = 8500

firing_order = [1, 6, 5, 10, 2, 7, 3, 8, 4, 9]

rpm_pattern = [
    900, 1300, 1800, 2500, 3400, 4500, 5600,
    6800, 7800, 8500, 8300, 8500, 8300,
    7600, 6500, 5200, 3900, 2700, 1700, 900
]

rpm = RPM_MIN
target_i = 0
last_target_change = time.time()

fire_i = 0
last_fire = time.time()

last_pitch_step = None
pitched_sound = None

last_rpm = rpm
last_burble_time = 0
BURBLE_COOLDOWN = 0.45

print("pizdec simulator")

try:
    while True:
        now = time.time()

        if now - last_target_change > 0.45:
            target_i = (target_i + 1) % len(rpm_pattern)
            last_target_change = now

        target_rpm = rpm_pattern[target_i]
        rpm += (target_rpm - rpm) * 0.035

        pitch = rpm / 700
        pitch = max(3, pitch)
        pitch_step = round(pitch * 10) / 10

        if pitch_step != last_pitch_step:
            pitched_sound = make_pitch_sound(base_array, pitch_step)
            pitched_sound.set_volume(0.10)
            last_pitch_step = pitch_step

        fires_per_second = rpm / 12.0
        fire_interval = 1.0 / fires_per_second

        if now - last_fire >= fire_interval:
            ch = pygame.mixer.find_channel()
            if ch and pitched_sound:
                ch.play(pitched_sound)

            fire_i = (fire_i + 1) % len(firing_order)
            last_fire = now

        rpm_drop = last_rpm - rpm

        if (
            rpm_drop > 35
            and 2200 < rpm < 7500
            and now - last_burble_time > BURBLE_COOLDOWN
            and random.random() < 0.35
        ):
            burble = random.choice(burble_sounds)
            ch = pygame.mixer.find_channel()
            if ch:
                ch.play(burble)
                print(" BURBLE")

            last_burble_time = now

        last_rpm = rpm

        print(
            f"\rRPM: {rpm:5.0f} | target: {target_rpm:5.0f} | cyl: {firing_order[fire_i]} | pitch: {pitch_step:.1f}",
            end="",
            flush=True
        )

        time.sleep(0.001)

except KeyboardInterrupt:
    pass

pygame.quit()