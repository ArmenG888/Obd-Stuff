import time
import obd
from obd import OBDCommand
from obd.protocols import ECU
from obd.decoders import noop

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

        time.sleep(0.1)

except KeyboardInterrupt:
    pass

connection.close()