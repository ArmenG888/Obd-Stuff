import obd
from obd import OBDCommand
from obd.protocols import ECU

# ---------- Helpers ----------

def signed(val):
    """Convert unsigned byte to signed"""
    return val - 256 if val > 127 else val


# ---------- Decoders ----------

def rear_motor_rpm(messages):
    data = messages[0].data
    # BB = index 53, BC = index 54
    bb = signed(data[53])
    bc = data[54]
    return bb * 256 + bc


def front_motor_rpm(messages):
    data = messages[0].data
    # BD = index 55, BE = index 56
    bd = signed(data[55])
    be = data[56]
    return bd * 256 + be


# ---------- OBD Commands ----------

REAR_RPM_CMD = OBDCommand(
    name="EV6_REAR_MOTOR_RPM",
    desc="EV6 Rear Motor RPM",
    command=b"\x22\x01\x01",
    bytes=64,                 # multi-frame response
    decoder=rear_motor_rpm,
    ecu=ECU.ALL
)

FRONT_RPM_CMD = OBDCommand(
    name="EV6_FRONT_MOTOR_RPM",
    desc="EV6 Front Motor RPM",
    command=b"\x22\x01\x01",
    bytes=64,
    decoder=front_motor_rpm,
    ecu=ECU.ALL
)


# ---------- Main ----------

def main():
    print("Connecting to OBD...")
    connection = obd.OBD(fast=False)

    # VERY IMPORTANT for Hyundai/Kia
    connection.connection.set_header("7E4")

    # Register commands
    connection.supported_commands.add(REAR_RPM_CMD)
    connection.supported_commands.add(FRONT_RPM_CMD)

    print("Reading motor RPM (Ctrl+C to stop)\n")

    try:
        while True:
            rear = connection.query(REAR_RPM_CMD)
            front = connection.query(FRONT_RPM_CMD)

            rear_rpm = rear.value if rear.value is not None else "N/A"
            front_rpm = front.value if front.value is not None else "N/A"

            print(f"Rear RPM: {rear_rpm} | Front RPM: {front_rpm}")

    except KeyboardInterrupt:
        print("\nStopped.")

    finally:
        connection.close()


if __name__ == "__main__":
    main()
