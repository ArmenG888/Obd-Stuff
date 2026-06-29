import sys, time, threading, random
import obd
import pygame

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
        self.last_throttle = 0
        self.last_gear = 0
        self.last_burble_time = 0
        self.last_rpm = 0

        self.COOLDOWN = 1.2       # seconds
        self.RPM_MIN = 800
        self.THROTTLE_DROP = 5   # %

    def update(self):
        try:
            rpm = connection.query(obd.commands.RPM)
            rpm = float(str(rpm.value).split(" ")[0])
            speed = connection.query(obd.commands.SPEED)
            speed = float(str(speed.value).split(" ")[0])
            throttle = connection.query(obd.commands.THROTTLE_POS)
            throttle = float(str(throttle.value).split(" ")[0])
            
            print(rpm, speed, throttle)

            #gear = estimate_gear(rpm, speed)

            now = time.time()
            throttle_drop = self.last_throttle - throttle
            #gear_changed = gear != self.last_gear

            # -------- BURBLE CONDITIONS --------
            if (rpm > self.RPM_MIN and throttle_drop > self.THROTTLE_DROP):
                heavy = rpm > 4000
                play_burble(heavy)
                print("burble")
                self.last_burble_time = now
            #if ((rpm - self.last_rpm) > 500) and (throttle < 20):
            #    play_burble(heavy)

            #if (throttle > 70)   and ((self.last_rpm - rpm) > 0):
            #    burble_shift.play()

            #if(gear != last_gear):
                #burble_shift.play()

            self.last_throttle = throttle
            self.last_rpm = rpm
        except Exception:
            pass

def run():
    burbler = Burbler()
    print("running")

    while True:
        burbler.update()
        time.sleep(0.1)


if __name__ == "__main__":
    run()