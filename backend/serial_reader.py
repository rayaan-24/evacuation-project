import argparse
import logging
import sys
import time

import requests
import serial

SUPPORTED_TYPES = {"FIRE", "SMOKE", "BLOCKAGE", "CROWD", "GAS"}

SERIAL_PORT = "COM3"
BAUD_RATE = 9600
API_URL = "http://localhost:5000/sensor-update"
READ_INTERVAL = 0.1
RECONNECT_DELAY_SECONDS = 3
POST_TIMEOUT_SECONDS = 3


logger = logging.getLogger("serial_reader")


def configure_logging(verbose=False):
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s | %(levelname)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )


def parse_arduino_message(raw_message):
    """Parse SENSOR:sensor_x,TYPE:FIRE style serial messages."""
    if not raw_message:
        return None
    
    message = raw_message.strip()
    
    # Ignore debug/status messages
    if message.startswith("DEBUG:") or message.startswith("INFO:") or message.startswith("TEST:") or message.startswith("STATUS:"):
        logger.debug("Arduino info message: %s", message)
        return None
    
    parts = [part.strip() for part in message.split(",") if part.strip()]
    values = {}

    for part in parts:
        if ":" not in part:
            continue
        key, value = part.split(":", 1)
        values[key.strip().upper()] = value.strip()

    sensor_id = values.get("SENSOR")
    emergency_type = values.get("TYPE", "").upper()

    if not sensor_id or not emergency_type:
        logger.warning("Invalid message format: %s", message)
        return None

    if emergency_type not in SUPPORTED_TYPES:
        logger.warning("Unsupported emergency type '%s' in message: %s", emergency_type, message)
        return None

    return {"sensor_id": sensor_id, "type": emergency_type}


def send_to_flask(data):
    """Send parsed emergency payload to Flask /sensor-update."""
    try:
        response = requests.post(API_URL, json=data, timeout=POST_TIMEOUT_SECONDS)
        if response.ok:
            logger.info("Forwarded emergency %s", data)
            return True

        logger.error("API rejected update. status=%s body=%s", response.status_code, response.text)
        return False
    except requests.exceptions.RequestException as exc:
        logger.error("Failed to call backend API: %s", exc)
        return False


def open_serial_connection(port, baud_rate):
    """Open serial connection with retry handling."""
    while True:
        try:
            connection = serial.Serial(port, baud_rate, timeout=1)
            time.sleep(2)
            logger.info("Connected to Arduino serial on %s @ %s", port, baud_rate)
            return connection
        except serial.SerialException as exc:
            logger.error("Serial connection failed on %s: %s", port, exc)
            logger.info("Retrying serial connection in %s seconds", RECONNECT_DELAY_SECONDS)
            time.sleep(RECONNECT_DELAY_SECONDS)


def run_serial_reader(port, baud_rate):
    """Read serial events forever and forward to backend."""
    logger.info("Starting serial reader. api=%s", API_URL)
    connection = open_serial_connection(port, baud_rate)

    while True:
        try:
            if connection.in_waiting > 0:
                raw_line = connection.readline().decode("utf-8", errors="ignore").strip()
                if not raw_line:
                    continue

                logger.debug("Raw serial line: %s", raw_line)
                parsed = parse_arduino_message(raw_line)
                if parsed:
                    send_to_flask(parsed)

            time.sleep(READ_INTERVAL)

        except KeyboardInterrupt:
            logger.info("Serial reader stopped by user")
            connection.close()
            break
        except serial.SerialException as exc:
            logger.error("Serial read error: %s", exc)
            try:
                connection.close()
            except Exception:
                pass
            connection = open_serial_connection(port, baud_rate)
        except Exception as exc:
            logger.exception("Unexpected reader error: %s", exc)
            time.sleep(1)


def run_demo_mode():
    """Send sample emergency events without Arduino hardware."""
    samples = [
        {"sensor_id": "sensor_0", "type": "FIRE"},
        {"sensor_id": "sensor_4", "type": "BLOCKAGE"},
        {"sensor_id": "sensor_8", "type": "SMOKE"},
        {"sensor_id": "sensor_12", "type": "CROWD"},
        {"sensor_id": "sensor_16", "type": "GAS"},
    ]

    logger.info("Running demo mode with %s events", len(samples))
    for payload in samples:
        logger.info("Demo send: %s", payload)
        send_to_flask(payload)
        time.sleep(1.5)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Arduino serial reader for multi-emergency updates")
    parser.add_argument("mode", nargs="?", default="live", choices=["live", "demo"])
    parser.add_argument("--port", default=SERIAL_PORT)
    parser.add_argument("--baud", default=BAUD_RATE, type=int)
    parser.add_argument("--verbose", action="store_true")
    args = parser.parse_args()

    configure_logging(verbose=args.verbose)

    if args.mode == "demo":
        run_demo_mode()
        sys.exit(0)

    run_serial_reader(args.port, args.baud)
