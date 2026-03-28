"""
serial_reader.py - Reads Arduino sensor data and sends to Flask
===============================================================
Think of this like a translator:
- Arduino speaks "Serial port language"  
- Flask speaks "HTTP/JSON language"
- This script translates between them!

How it works:
1. Arduino sends: "SENSOR:sensor_1,SMOKE:450,FLAME:1"
2. This script reads that from USB port
3. Converts to JSON and sends to Flask API
4. Flask updates the map automatically!
"""

import serial
import requests
import time
import json
import sys

# ============================================================
# SETTINGS - Change these to match your system
# ============================================================
SERIAL_PORT = "COM3"       # Windows: COM3, COM4, etc.
                            # Linux/Mac: /dev/ttyUSB0 or /dev/ttyACM0
BAUD_RATE = 9600           # Must match Arduino code
API_URL = "http://localhost:5000/sensor-update"
READ_INTERVAL = 0.5        # Read every 0.5 seconds
# ============================================================


def parse_arduino_message(raw_message):
    """
    Parse the string from Arduino into a Python dictionary.
    
    Input:  "SENSOR:sensor_1,SMOKE:450,FLAME:1"
    Output: {"sensor_id": "sensor_1", "smoke": 450, "flame": 1}
    """
    try:
        parts = raw_message.strip().split(",")
        parsed = {}

        for part in parts:
            if ":" in part:
                key, value = part.split(":", 1)
                key = key.strip().lower()

                if key == "sensor":
                    parsed["sensor_id"] = value.strip()
                elif key == "smoke":
                    parsed["smoke"] = int(value.strip())
                elif key == "flame":
                    parsed["flame"] = int(value.strip())

        # Validate that we got all required fields
        if "sensor_id" in parsed and "smoke" in parsed:
            return parsed
        else:
            return None

    except Exception as e:
        print(f"[PARSE ERROR] Could not parse: '{raw_message}' | Error: {e}")
        return None


def send_to_flask(data):
    """
    Send sensor data to Flask API.
    Returns True if successful, False otherwise.
    """
    try:
        response = requests.post(
            API_URL,
            json=data,
            timeout=2  # 2 second timeout
        )

        if response.status_code == 200:
            result = response.json()
            fire_status = "🔥 FIRE DETECTED!" if data.get("flame") == 1 else "✅ Normal"
            print(f"[SENT] Sensor: {data['sensor_id']} | "
                  f"Smoke: {data.get('smoke', '?')} | "
                  f"Flame: {data.get('flame', '?')} | {fire_status}")
            return True
        else:
            print(f"[API ERROR] Status: {response.status_code}")
            return False

    except requests.exceptions.ConnectionError:
        print("[ERROR] Cannot connect to Flask. Is app.py running?")
        return False
    except Exception as e:
        print(f"[ERROR] {e}")
        return False


def run_serial_reader():
    """Main loop - continuously read from Arduino and send to Flask"""
    print("=" * 50)
    print("🔌 Arduino Serial Reader Started")
    print(f"   Port: {SERIAL_PORT}")
    print(f"   Baud: {BAUD_RATE}")
    print(f"   API: {API_URL}")
    print("   Press Ctrl+C to stop")
    print("=" * 50)

    # Try to open serial port
    try:
        ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
        print(f"✅ Connected to Arduino on {SERIAL_PORT}")
        time.sleep(2)  # Wait for Arduino to initialize

    except serial.SerialException as e:
        print(f"❌ Cannot open port {SERIAL_PORT}: {e}")
        print("\nTROUBLESHOOTING:")
        print("  1. Check if Arduino is connected via USB")
        print("  2. Check correct port name (Device Manager on Windows)")
        print("  3. Make sure no other program is using this port")
        sys.exit(1)

    # Main reading loop
    print("\n📡 Reading sensor data...\n")
    consecutive_errors = 0

    while True:
        try:
            # Read one line from Arduino
            if ser.in_waiting > 0:
                raw = ser.readline().decode("utf-8", errors="ignore")

                if raw.strip():  # If not empty
                    print(f"[RAW] {raw.strip()}")
                    data = parse_arduino_message(raw)

                    if data:
                        send_to_flask(data)
                        consecutive_errors = 0
                    else:
                        print(f"[SKIP] Could not parse message")

            time.sleep(READ_INTERVAL)

        except KeyboardInterrupt:
            print("\n\n👋 Stopped by user")
            ser.close()
            break

        except Exception as e:
            consecutive_errors += 1
            print(f"[ERROR] {e} (error #{consecutive_errors})")

            if consecutive_errors > 10:
                print("Too many errors. Stopping.")
                ser.close()
                sys.exit(1)

            time.sleep(1)


# ============================================================
# DEMO MODE - Run without Arduino (for testing)
# ============================================================
def run_demo_mode():
    """
    Test without Arduino - sends fake sensor data.
    Usage: python serial_reader.py demo
    """
    print("=" * 50)
    print("🧪 DEMO MODE (No Arduino needed)")
    print("=" * 50)

    import random

    scenarios = [
        {"sensor_id": "sensor_1", "smoke": 50,  "flame": 0},  # Normal
        {"sensor_id": "sensor_2", "smoke": 100, "flame": 0},  # Slight smoke
        {"sensor_id": "sensor_2", "smoke": 350, "flame": 0},  # Heavy smoke
        {"sensor_id": "sensor_2", "smoke": 500, "flame": 1},  # FIRE!
        {"sensor_id": "sensor_3", "smoke": 80,  "flame": 0},  # Normal
    ]

    for scenario in scenarios:
        print(f"\n[DEMO] Sending: {scenario}")
        send_to_flask(scenario)
        time.sleep(2)

    print("\n✅ Demo complete!")


# ============================================================
if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "demo":
        run_demo_mode()
    else:
        run_serial_reader()
