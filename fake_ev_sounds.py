import gpsd

gpsd.connect()

def get_speed_kmh():
    packet = gpsd.get_current()
    if packet.mode >= 2:
        return packet.speed() * 3.6  # m/s → km/h
    return 0
