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

connection = obd.OBD(fast=False, timeout=2)
response = connection.query(RAW_220101)

print(response.value)
connection.close()