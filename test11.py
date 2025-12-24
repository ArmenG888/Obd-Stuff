import obd
import os
connection = obd.OBD("COM8")

if not connection.is_connected():
	print("nla")
	exit()

print("good")


supported = connection.supported_commands
#print(supported)
for cmd in supported:
	resp = connection.query(cmd)
	print(f"{cmd.name} {resp.value}")

#for i in range(1000):
	#cmd = obd.commands.RPM
	#response = connection.query(cmd)
	#print(response.value)
	