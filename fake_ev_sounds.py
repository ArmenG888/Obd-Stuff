import sys, time, threading, random
import obd
import pygame
from obd import OBDCommand
from obd.protocols import ECU
from obd.decoders import noop

connection = obd.OBD("COM8", fast=False, timeout=2)

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

def signed_16(high, low):
    raw = (high << 8) + low
    return raw - 65536 if raw >= 32768 else raw

def get_battery_kw():
    try:
        r = connection.query(RAW_220101, force=True)

        if r.is_null():
            return 0

        data = r.value
        d = data[3:]  # remove 62 01 01

        amps = signed_16(d[10], d[11]) / 10
        volts = ((d[12] << 8) + d[13]) / 10
        kw = amps * volts / 1000

        # flip this if accel is negative on your car
        return kw

    except Exception:
        return 0


pygame.mixer.init()

burble_short  = pygame.mixer.Sound("burble_short.mp3")
burble_shift  = pygame.mixer.Sound("burble_shift.mp3")
burble_medium = pygame.mixer.Sound("burble_medium.mp3")
burble_long   = pygame.mixer.Sound("burble_long.mp3")
burble_long2  = pygame.mixer.Sound("burble_really_long.mp3")

LIGHT_BURBLES = [burble_short, burble_shift]
HEAVY_BURBLES = [burble_medium, burble_long, burble_long2]

def play_burble(heavy=False):
    sound = random.choice(HEAVY_BURBLES if heavy else LIGHT_BURBLES)
    sound.play()


class Burbler:
    def __init__(self):
        self.last_kw = 0
        self.last_burble_time = 0

        self.COOLDOWN = 1.0
        self.KW_DROP = 0.3       # burble when power drops by this much
        self.MIN_KW_BEFORE = 0 # must have been using power before lift

    def update(self):
        kw = get_battery_kw()
        now = time.time()

        kw_drop = self.last_kw - kw

        print(f"\rKW: {kw:.1f} | drop: {kw_drop:.1f}", end="", flush=True)

        if (
            self.last_kw > self.MIN_KW_BEFORE
            and kw_drop > self.KW_DROP
            and now - self.last_burble_time > self.COOLDOWN
        ):
            heavy = self.last_kw > 40 or kw_drop > 25
            play_burble(heavy)
            print("  BURBLE")
            self.last_burble_time = now

        self.last_kw = kw


def run():
    burbler = Burbler()
    print("running")

    while True:
        burbler.update()
        time.sleep(0.1)


if __name__ == "__main__":
    run()