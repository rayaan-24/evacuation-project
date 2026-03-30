import logging
import os
import sys
import time
from typing import Dict, List

from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pathfinder import load_layout, run_pathfinder

SUPPORTED_TYPES = {"FIRE", "SMOKE", "BLOCKAGE", "CROWD", "GAS"}
EMERGENCY_TIMEOUT_SECONDS = int(os.getenv("EMERGENCY_TIMEOUT_SECONDS", "0"))

app = Flask(__name__)
CORS(app)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("app")

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LAYOUT_PATH = os.path.join(PROJECT_ROOT, "data", "building_layout.json")

layout_cache = load_layout(LAYOUT_PATH)
sensor_map = layout_cache.get("sensor_map", {})

# In-memory real-time state. For production, persist this in a database.
active_emergencies: List[Dict] = []


def normalize_emergency_type(value):
    emergency_type = str(value or "").strip().upper()
    return emergency_type if emergency_type in SUPPORTED_TYPES else None


def cleanup_expired_emergencies():
    if EMERGENCY_TIMEOUT_SECONDS <= 0:
        return

    now = time.time()
    before = len(active_emergencies)
    active_emergencies[:] = [
        event for event in active_emergencies
        if now - event.get("updated_at", now) <= EMERGENCY_TIMEOUT_SECONDS
    ]
    expired = before - len(active_emergencies)
    if expired:
        logger.info("Auto-cleared %s expired emergency event(s)", expired)


def upsert_emergency(sensor_id, location, emergency_type):
    now = time.time()
    for event in active_emergencies:
        if event.get("sensor_id") == sensor_id:
            event.update({
                "sensor_id": sensor_id,
                "location": location,
                "type": emergency_type,
                "updated_at": now,
            })
            return event

    event = {
        "sensor_id": sensor_id,
        "location": location,
        "type": emergency_type,
        "updated_at": now,
    }
    active_emergencies.append(event)
    return event


@app.after_request
def disable_cache(response):
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response


@app.route("/")
def home():
    return send_from_directory(PROJECT_ROOT, "frontend/smart_evacuation_demo.html")


@app.route("/api")
def api_home():
    return jsonify({
        "message": "Smart Evacuation System API",
        "status": "running",
        "frontend": "/",
        "supported_emergencies": sorted(SUPPORTED_TYPES),
        "timeout_seconds": EMERGENCY_TIMEOUT_SECONDS,
        "endpoints": [
            "/layout",
            "/find-path",
            "/sensor-update",
            "/sensor-status",
            "/reset-emergencies",
        ],
    })


@app.route("/layout", methods=["GET"])
def get_layout():
    return jsonify(load_layout(LAYOUT_PATH))


@app.route("/find-path", methods=["POST"])
def find_path():
    data = request.get_json(silent=True) or {}
    start_room = data.get("start_room")

    if not start_room:
        return jsonify({"error": "start_room is required"}), 400

    cleanup_expired_emergencies()

    requested_emergencies = data.get("emergencies")
    include_active = data.get("include_active", True)

    merged = []
    if include_active:
        merged.extend({"location": e["location"], "type": e["type"]} for e in active_emergencies)

    if isinstance(requested_emergencies, list):
        merged.extend(requested_emergencies)
    else:
        # Backward compatibility for older frontend payloads.
        for location in data.get("fire_locations") or data.get("fire_rooms", []):
            merged.append({"location": location, "type": "FIRE"})

    unique_emergencies = []
    seen = set()
    for item in merged:
        location = str(item.get("location", "")).strip()
        emergency_type = normalize_emergency_type(item.get("type"))
        key = (location, emergency_type)
        if location and emergency_type and key not in seen:
            seen.add(key)
            unique_emergencies.append({"location": location, "type": emergency_type})

    logger.info("Path request start=%s emergencies=%s", start_room, unique_emergencies)
    result = run_pathfinder(start_room, unique_emergencies, LAYOUT_PATH)
    return jsonify(result)


@app.route("/sensor-update", methods=["POST"])
def sensor_update():
    data = request.get_json(silent=True) or {}
    sensor_id = str(data.get("sensor_id", "")).strip()
    emergency_type = normalize_emergency_type(data.get("type"))

    if not sensor_id:
        return jsonify({"error": "sensor_id is required"}), 400
    if not emergency_type:
        return jsonify({"error": f"type must be one of {sorted(SUPPORTED_TYPES)}"}), 400

    location = sensor_map.get(sensor_id)
    if not location:
        return jsonify({"error": f"Unknown sensor_id: {sensor_id}"}), 400

    cleanup_expired_emergencies()
    event = upsert_emergency(sensor_id, location, emergency_type)

    logger.info("Sensor update sensor=%s location=%s type=%s", sensor_id, location, emergency_type)
    return jsonify({
        "status": "updated",
        "event": {
            "sensor_id": event["sensor_id"],
            "location": event["location"],
            "type": event["type"],
            "updated_at": event["updated_at"],
        },
    })


@app.route("/sensor-status", methods=["GET"])
def sensor_status():
    cleanup_expired_emergencies()

    return jsonify({
        "active_emergencies": [
            {
                "sensor_id": event["sensor_id"],
                "location": event["location"],
                "type": event["type"],
                "updated_at": event["updated_at"],
            }
            for event in active_emergencies
        ],
        "total_active": len(active_emergencies),
        "alert": len(active_emergencies) > 0,
    })


@app.route("/reset-emergencies", methods=["POST"])
def reset_emergencies():
    data = request.get_json(silent=True) or {}
    sensor_id = data.get("sensor_id")
    location = data.get("location")

    if sensor_id:
        before = len(active_emergencies)
        active_emergencies[:] = [event for event in active_emergencies if event.get("sensor_id") != sensor_id]
        removed = before - len(active_emergencies)
    elif location:
        before = len(active_emergencies)
        active_emergencies[:] = [event for event in active_emergencies if event.get("location") != location]
        removed = before - len(active_emergencies)
    else:
        removed = len(active_emergencies)
        active_emergencies.clear()

    logger.info("Reset emergencies removed=%s sensor_id=%s location=%s", removed, sensor_id, location)
    return jsonify({"status": "reset", "removed": removed, "remaining": len(active_emergencies)})


@app.route("/simulate-sensor", methods=["POST"])
def simulate_sensor():
    data = request.get_json(silent=True) or {}
    sensor_id = str(data.get("sensor_id", "")).strip()
    emergency_type = normalize_emergency_type(data.get("type", "FIRE"))
    active = bool(data.get("active", True))

    if sensor_id not in sensor_map:
        return jsonify({"error": f"Unknown sensor_id: {sensor_id}"}), 400

    if active:
        event = upsert_emergency(sensor_id, sensor_map[sensor_id], emergency_type)
        logger.info("Simulated ON %s", event)
        return jsonify({"status": "simulated_on", "event": event})

    before = len(active_emergencies)
    active_emergencies[:] = [event for event in active_emergencies if event.get("sensor_id") != sensor_id]
    logger.info("Simulated OFF sensor=%s removed=%s", sensor_id, before - len(active_emergencies))
    return jsonify({"status": "simulated_off", "sensor_id": sensor_id})


@app.route("/simulation/run", methods=["POST"])
def run_simulation():
    """Run multi-agent evacuation simulation"""
    try:
        from simulation import EvacuationSimulator
        from pathfinder import build_graph
        
        data = request.get_json(silent=True) or {}
        rooms = data.get("rooms", ["G01", "G07", "G11", "G13"])
        danger_zones = data.get("danger_zones", [])
        max_time = float(data.get("max_time", 300))
        
        layout = load_layout(LAYOUT_PATH)
        graph = build_graph(layout)
        
        simulator = EvacuationSimulator(layout, graph)
        simulator.add_people(rooms)
        results = simulator.run_simulation(
            max_time=max_time,
            danger_nodes=set(danger_zones)
        )
        
        return jsonify({
            "success": True,
            "results": results
        })
    except Exception as e:
        logger.error("Simulation error: %s", str(e))
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/simulation/stats", methods=["GET"])
def simulation_stats():
    """Get ACO auto-tuning recommendations"""
    try:
        from auto_tune import ACOAutoTuner
        from pathfinder import build_graph
        
        layout = load_layout(LAYOUT_PATH)
        graph = build_graph(layout)
        
        tuner = ACOAutoTuner(graph, layout)
        recommendations = tuner.get_tuning_recommendations()
        
        return jsonify({
            "success": True,
            "recommendations": recommendations
        })
    except Exception as e:
        logger.error("Auto-tune error: %s", str(e))
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/version", methods=["GET"])
def version():
    """Get system version info"""
    return jsonify({
        "system": "Smart Evacuation System",
        "version": "2.0.0",
        "aco_mode": "enhanced",
        "algorithms": ["ACO", "Dijkstra", "A*"]
    })


if __name__ == "__main__":
    logger.info("Smart Evacuation backend listening at http://localhost:5000")
    logger.info("Emergency timeout is %s seconds (0 disables auto-clear)", EMERGENCY_TIMEOUT_SECONDS)
    app.run(debug=True, host="0.0.0.0", port=5000)
