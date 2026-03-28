"""
app.py - Flask Backend API
===========================
This is the brain of the system.
It receives requests from the frontend and returns paths.

Think of it like a waiter:
- Frontend asks: "Find path from Room 1, fire in Room 2"
- This waiter goes to the kitchen (ACO algorithm)
- Brings back the answer (path + directions)
"""

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import json
import os
import sys

# Make sure we can import our own files
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pathfinder import run_pathfinder, load_layout

app = Flask(__name__)
CORS(app)  # Allow frontend (different port) to talk to this backend

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LAYOUT_PATH = os.path.join(PROJECT_ROOT, "data", "building_layout.json")


def build_sensor_state():
    """Initialize sensor state from the JSON layout sensor map."""
    layout = load_layout(LAYOUT_PATH)
    sensor_map = layout.get("sensor_map", {})
    return {
        sensor_id: {"smoke": 0, "flame": 0, "location": room_id}
        for sensor_id, room_id in sensor_map.items()
    }


# Store IoT sensor data in memory (in production, use a database)
sensor_data = build_sensor_state()


@app.route("/")
def home():
    """Serve the frontend demo page at the root URL."""
    return send_from_directory(PROJECT_ROOT, "smart_evacuation_demo.html")


@app.route("/api")
def api_home():
    """Simple welcome message for the backend API."""
    return jsonify({
        "message": "Smart Evacuation System API",
        "status": "running",
        "frontend": "/",
        "endpoints": ["/layout", "/find-path", "/sensor-update", "/sensor-status"]
    })


@app.route("/layout", methods=["GET"])
def get_layout():
    """
    Returns the building layout JSON.
    Frontend uses this to draw the map.
    """
    layout = load_layout(LAYOUT_PATH)
    return jsonify(layout)


@app.route("/find-path", methods=["POST"])
def find_path():
    """
    Main endpoint: Find evacuation path.
    
    Frontend sends:
    {
        "start_room": "G07",
        "fire_rooms": ["G17"],
        "emergency_type": "fire"
    }
    
    Returns: path, directions, distance
    """
    data = request.get_json()

    if not data:
        return jsonify({"error": "No data received"}), 400

    start_room = data.get("start_room")
    fire_rooms = data.get("fire_locations") or data.get("fire_rooms", [])
    emergency_type = data.get("emergency_type", "fire")

    if not start_room:
        return jsonify({"error": "start_room is required"}), 400

    print(f"\n[API] Path request: start={start_room}, fire={fire_rooms}")

    # Build layout path
    # Run the ACO pathfinder
    result = run_pathfinder(start_room, fire_rooms, LAYOUT_PATH)
    result["emergency_type"] = emergency_type

    return jsonify(result)


@app.route("/sensor-update", methods=["POST"])
def sensor_update():
    """
    Arduino sends sensor readings here.
    
    Arduino sends:
    {
        "sensor_id": "sensor_1",
        "smoke": 450,
        "flame": 1
    }
    
    flame = 1 means fire detected!
    smoke > 300 means heavy smoke!
    """
    data = request.get_json()

    if not data:
        return jsonify({"error": "No data"}), 400

    sensor_id = data.get("sensor_id")
    if sensor_id not in sensor_data:
        return jsonify({"error": f"Unknown sensor: {sensor_id}"}), 400

    # Update sensor readings
    sensor_data[sensor_id]["smoke"] = data.get("smoke", 0)
    sensor_data[sensor_id]["flame"] = data.get("flame", 0)

    print(f"[IoT] Sensor {sensor_id}: smoke={data.get('smoke')}, flame={data.get('flame')}")

    return jsonify({"status": "updated", "sensor": sensor_id})


@app.route("/sensor-status", methods=["GET"])
def sensor_status():
    """
    Frontend polls this to get current fire locations from IoT sensors.
    Returns list of rooms where fire/smoke is detected.
    """
    fire_rooms = []

    for sensor_id, readings in sensor_data.items():
        is_fire = readings["flame"] == 1 or readings["smoke"] > 300
        if is_fire:
            fire_rooms.append(readings["location"])

    return jsonify({
        "sensors": sensor_data,
        "fire_detected_rooms": fire_rooms,
        "alert": len(fire_rooms) > 0
    })


@app.route("/simulate-sensor", methods=["POST"])
def simulate_sensor():
    """
    For testing without real Arduino.
    Simulates a sensor detecting fire.
    
    Send: { "sensor_id": "sensor_1", "fire": true }
    """
    data = request.get_json()
    sensor_id = data.get("sensor_id")
    fire = data.get("fire", False)

    if sensor_id in sensor_data:
        sensor_data[sensor_id]["smoke"] = 500 if fire else 50
        sensor_data[sensor_id]["flame"] = 1 if fire else 0
        return jsonify({"status": "simulated", "sensor": sensor_id, "fire": fire})

    return jsonify({"error": "Unknown sensor"}), 400


if __name__ == "__main__":
    print("=" * 50)
    print("🚀 Smart Evacuation System Backend")
    print("   Running at http://localhost:5000")
    print("   Press Ctrl+C to stop")
    print("=" * 50)
    app.run(debug=True, host="0.0.0.0", port=5000)
