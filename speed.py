import time
import obd
from obd import OBDCommand
from obd.protocols import ECU
from obd.decoders import noop

RAW_SPEED = OBDCommand(
    "KIA_REAL_SPEED",
    "Kia Real Vehicle Speed",
    b"220100",
    40,
    noop,
    ECU.ALL,
    False,
    header=b"7B3"
)

connection = obd.OBD("COM8", fast=False, timeout=2)

try:
    while True:
        r = connection.query(RAW_SPEED, force=True)

        if r.is_null():
            print("NO DATA")
            time.sleep(0.2)
            continue

        data = r.value

        # remove response header: 62 01 00
        d = data[3:]

        # AD = byte index 29 if A=0
        kmh = d[29]
        mph = kmh * 0.621371

        print(f"\rSpeed: {kmh:.0f} km/h | {mph:.1f} mph", end="", flush=True)

        time.sleep(0.1)

except KeyboardInterrupt:
    pass

connection.close()