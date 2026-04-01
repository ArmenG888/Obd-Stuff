import obd
import os, time, requests
from datetime import datetime
connection = obd.OBD("COM8")

if not connection.is_connected():
	print("nla")
	exit()

print("good")

url = "http://192.168.1.10:8000/upload"

#supported = connection.supported_commands
#print(supported)
#for cmd in supported:
	#resp = connection.query(cmd)
	#print(f"{cmd.name} {resp.value}")

while True:
	try:
		for i in range(10):
			cmd = obd.commands.ELM_VOLTAGE
			response = connection.query(cmd)
			voltage = str(response.value)
			data = {
				"timestamp": datetime.now().strftime("%m/%d/%Y %H:%M"),
				"voltage": voltage
			}
			response = requests.post(url, json=data)
			print(response.json())
			time.sleep(0.1)
	except Exception as e:
		print(e)
	time.sleep(10)
	