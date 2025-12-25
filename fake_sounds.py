import sys, time, threading, random
import obd
import pygame

# =======================
# OBD SETUP
# =======================
connection = obd.OBD("COM8")

def obd_command(command, type="float"):
    try:
        response = connection.query(command)
        if response.is_null():
            return 0
        value = response.value
        return float(value)
    except:
        return 0


# =======================
# AUDIO SETUP
# =======================
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


# =======================
# GEAR ESTIMATION
# =======================
def estimate_gear(rpm, speed_kmh, tire_circ_m=2.32, final_drive=3.320):
    ratios = {
        1: 4.808 * final_drive,
        2: 2.901 * final_drive,
        3: 1.864 * final_drive,
        4: 1.424 * final_drive,
        5: 1.219 * final_drive,
        6: 1.000 * final_drive,
        7: 0.799 * final_drive,
        8: 0.648 * final_drive,
    }

    if speed_kmh < 5:
        return 0

    combined = (rpm * tire_circ_m * 60) / (1000 * speed_kmh)
    return min(ratios, key=lambda g: abs(ratios[g] - combined))


# =======================
# BURBLER LOGIC
# =======================
class Burbler:
    def __init__(self):
        self.last_throttle = 0
        self.last_gear = 0
        self.last_burble_time = 0

        self.COOLDOWN = 1.2       # seconds
        self.RPM_MIN = 800
        self.THROTTLE_DROP = 0.3   # %

    def update(self):
        rpm = connection.query(obd.commands.RPM)
        rpm = float(str(rpm.value).split(" ")[0])
        speed = connection.query(obd.commands.SPEED)
        speed = float(str(speed.value).split(" ")[0])
        throttle = connection.query(obd.commands.THROTTLE_POS)
        throttle = float(str(throttle.value).split(" ")[0])
        
        print(rpm, speed, throttle)

        gear = estimate_gear(rpm, speed)

        now = time.time()
        throttle_drop = self.last_throttle - throttle
        gear_changed = gear != self.last_gear

        # -------- BURBLE CONDITIONS --------
        if (
            rpm > self.RPM_MIN and
            throttle_drop > self.THROTTLE_DROP and
            now - self.last_burble_time > self.COOLDOWN
        ):
            heavy = rpm > 1000 or gear_changed
            play_burble(heavy)
            print("burble")
            self.last_burble_time = now

        self.last_throttle = throttle
        self.last_gear = gear


# =======================
# MAIN LOOP
# =======================
def run():
    burbler = Burbler()
    print("🔥 Burbler running...")

    while True:
        burbler.update()
        time.sleep(0.1)


if __name__ == "__main__":
    run()