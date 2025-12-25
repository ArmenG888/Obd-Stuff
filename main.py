import obd
from obd import OBDCommand
from obd.protocols import ECU

def signed(b):
    return b - 256 if b > 127 else b

def rear_motor_rpm(messages):
    data = messages[0].data
    return signed(data[53]) * 256 + data[54]

def front_motor_rpm(messages):
    data = messages[0].data
    return signed(data[55]) * 256 + data[56]

connection = obd.OBD("COM8", fast=False)

if not connection.is_connected():
    print("nla")
    exit()

print("good")

# REQUIRED for Hyundai/Kiav
connection.connection.set_header("7E4")

# Register custom commands
connection.supported_commands.add(REAR_RPM := OBDCommand(
    "EV6_REAR_MOTOR_RPM",
    "EV6 Rear Motor RPM",
    b"\x22\x01\x01",
    64,
    rear_motor_rpm,
    ECU.ALL
))

connection.supported_commands.add(FRONT_RPM := OBDCommand(
    "EV6_FRONT_MOTOR_RPM",
    "EV6 Front Motor RPM",
    b"\x22\x01\x01",
    64,
    front_motor_rpm,
    ECU.ALL
))

# ---- LIVE READ ----
while True:
    rear = connection.query(REAR_RPM).value
    front = connection.query(FRONT_RPM).value
    print(f"Rear RPM: {rear} | Front RPM: {front}")
