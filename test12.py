import obd
from obd import OBDCommand
from obd.protocols import ECU
from obd.decoders import raw_string

RAW_220101 = OBDCommand(
    "RAW_220101",
    "Raw BMS 220101",
    b"220101",
    60,
    raw_string,
    ECU.ALL,
    False,
    header=b"7E4"
)

connection = obd.OBD("COM8")

if not connection.is_connected():
    print("nla")
    exit()

print("good")

response = connection.query(RAW_220101,force=True)

print(response.value)
connection.close()