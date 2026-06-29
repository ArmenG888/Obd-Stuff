from fastapi import FastAPI
from pydantic import BaseModel
import os
from datetime import datetime

app = FastAPI()

FILE = "db.csv"
ERROR_LOG = "error.log"

# ---------- INIT FILE ----------
def init_file():
    if not os.path.exists(FILE):
        with open(FILE, "w") as f:
            f.write("id,timestamp,voltage\n")

def log_error(e):
    with open(ERROR_LOG, "a") as f:
        f.write(f"{datetime.now()} | {str(e)}\n")

def get_next_id():
    with open(FILE, "r") as f:
        lines = f.readlines()
        return len(lines)  # header = line 1 → first data row = id 1

def get_row_count():
    with open(FILE, "r") as f:
        lines = f.readlines()
        return max(0, len(lines) - 1)  # exclude header

init_file()

# ---------- DATA MODEL ----------
class DataPayload(BaseModel):
    timestamp: str
    voltage: str

# ---------- API ----------
@app.post("/upload")
def upload_json(data: DataPayload):
    try:
        # 🔎 DEBUG PRINT
        print("Received JSON:")
        print("Timestamp:", data.timestamp)
        print("Voltage:", data.voltage)

        entry_id = get_next_id()

        # ✍️ Append to file
        with open(FILE, "a") as f:
            f.write(f"{entry_id},{data.timestamp},{data.voltage}\n")

        return {
            "message": "Saved to file",
            "id": entry_id,
            "timestamp": data.timestamp,
            "voltage": data.voltage
        }

    except Exception as e:
        log_error(e)
        return {
            "error": "Failed to save data",
            "details": str(e)
        }


# ---------- STATS ENDPOINT ----------
@app.get("/stats")
def stats():
    try:
        count = get_row_count()
        return {
            "rows": count
        }
    except Exception as e:
        log_error(e)
        return {
            "error": "Failed to read file",
            "details": str(e)
        }
