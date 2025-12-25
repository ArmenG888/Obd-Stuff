import sys, time, threading, random
import obd
import pygame

# =======================
# OBD SETUP
# =======================
connection = obd.OBD("COM8")

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
        self.last_speed = 0


    def update(self):
        speed = connection.query(obd.commands.SPEED)
        speed = float(str(speed.value).split(" ")[0])
        
        speed_delta = self.last_speed - speed

        if (speed_delta > 0 and speed_delta < 3):
            play_burble(True)
            print("burble")


        self.last_speed = speed


# =======================
# MAIN LOOP
# =======================
def run():
    burbler = Burbler()
    print("🔥 Burbler running...")

    while True:
        burbler.update()
        time.sleep(1)


if __name__ == "__main__":
    run()