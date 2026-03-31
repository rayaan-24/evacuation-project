import logging
import os
import sys
import time
from datetime import datetime
from typing import Dict, List, Optional

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

# ESP32 Device Registry
esp32_devices: Dict[str, Dict] = {}


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
        # For ESP32 devices, we might get unknown sensor IDs
        # Fallback to using the sensor_id as location
        location = sensor_id
        logger.warning("Unknown sensor_id: %s, using as location", sensor_id)

    cleanup_expired_emergencies()
    event = upsert_emergency(sensor_id, location, emergency_type)
    
    # Track source (ESP32 vs Serial)
    source = data.get("source", data.get("device_id", "unknown"))
    event["source"] = source

    logger.info("Sensor update sensor=%s location=%s type=%s source=%s", 
                sensor_id, location, emergency_type, source)
    
    return jsonify({
        "status": "updated",
        "event": {
            "sensor_id": event["sensor_id"],
            "location": event["location"],
            "type": event["type"],
            "updated_at": event["updated_at"],
            "source": source,
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
                "source": event.get("source", "unknown"),
            }
            for event in active_emergencies
        ],
        "total_active": len(active_emergencies),
        "alert": len(active_emergencies) > 0,
        "esp32_devices": {
            "total": len(esp32_devices),
            "online": sum(1 for d in esp32_devices.values() 
                         if time.time() - d.get("last_seen", 0) < 120)
        }
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


# ============================================================
# ESP32 Device Management Endpoints
# ============================================================

@app.route("/esp32/register", methods=["POST"])
def esp32_register():
    """
    Register an ESP32 device when it connects.
    
    Payload:
    {
        "device_id": "ESP32-001",
        "location": "Floor 1 - North Wing",
        "ip_address": "192.168.1.101",
        "wifi_ssid": "MyWiFi",
        "button_count": 30,
        "firmware_version": "1.0"
    }
    """
    data = request.get_json(silent=True) or {}
    
    device_id = data.get("device_id")
    if not device_id:
        return jsonify({"error": "device_id is required"}), 400
    
    now = time.time()
    
    esp32_devices[device_id] = {
        "device_id": device_id,
        "location": data.get("location", "Unknown"),
        "ip_address": data.get("ip_address"),
        "wifi_ssid": data.get("wifi_ssid"),
        "button_count": data.get("button_count", 30),
        "firmware_version": data.get("firmware_version", "1.0"),
        "registered_at": now,
        "last_seen": now,
        "status": "online",
        "total_triggers": 0,
        "online_duration_seconds": 0
    }
    
    logger.info("ESP32 registered: %s @ %s (%s)", device_id, 
                data.get("ip_address"), data.get("location"))
    
    return jsonify({
        "status": "registered",
        "device_id": device_id,
        "message": "Device registered successfully",
        "server_time": now
    }), 201


@app.route("/esp32/heartbeat", methods=["POST"])
def esp32_heartbeat():
    """
    Receive heartbeat from ESP32 device.
    
    Payload:
    {
        "device_id": "ESP32-001",
        "rssi": -45,
        "uptime_ms": 3600000,
        "total_triggers": 150
    }
    """
    data = request.get_json(silent=True) or {}
    
    device_id = data.get("device_id")
    if not device_id:
        return jsonify({"error": "device_id is required"}), 400
    
    if device_id in esp32_devices:
        esp32_devices[device_id]["last_seen"] = time.time()
        esp32_devices[device_id]["rssi"] = data.get("rssi")
        esp32_devices[device_id]["uptime_ms"] = data.get("uptime_ms")
        esp32_devices[device_id]["total_triggers"] = data.get("total_triggers", 0)
        esp32_devices[device_id]["status"] = "online"
        
        return jsonify({
            "status": "ok",
            "device_id": device_id,
            "server_time": time.time()
        })
    
    return jsonify({
        "status": "unknown_device",
        "device_id": device_id,
        "message": "Device not registered. Please register first."
    }), 404


@app.route("/esp32/devices", methods=["GET"])
def esp32_list_devices():
    """Get list of all registered ESP32 devices"""
    devices = []
    now = time.time()
    
    for device_id, info in esp32_devices.items():
        # Update online duration
        if "registered_at" in info:
            info["online_duration_seconds"] = now - info["registered_at"]
        
        # Check if device is stale (no heartbeat for 2 minutes)
        last_seen = info.get("last_seen", 0)
        if now - last_seen > 120:
            info["status"] = "offline"
        
        devices.append(info)
    
    return jsonify({
        "devices": devices,
        "total": len(devices),
        "online": sum(1 for d in devices if d.get("status") == "online"),
        "offline": sum(1 for d in devices if d.get("status") == "offline")
    })


@app.route("/esp32/devices/<device_id>", methods=["GET"])
def esp32_get_device(device_id):
    """Get info about specific ESP32 device"""
    if device_id not in esp32_devices:
        return jsonify({"error": "Device not found"}), 404
    
    info = esp32_devices[device_id].copy()
    info["online_duration_seconds"] = time.time() - info.get("registered_at", time.time())
    
    return jsonify(info)


@app.route("/esp32/devices/<device_id>", methods=["DELETE"])
def esp32_unregister_device(device_id):
    """Unregister an ESP32 device"""
    if device_id in esp32_devices:
        del esp32_devices[device_id]
        logger.info("ESP32 unregistered: %s", device_id)
        return jsonify({
            "status": "unregistered",
            "device_id": device_id
        })
    
    return jsonify({"error": "Device not found"}), 404


@app.route("/esp32/status", methods=["GET"])
def esp32_status():
    """Get ESP32 system status"""
    now = time.time()
    
    devices_by_status = {
        "online": [],
        "offline": []
    }
    
    for device_id, info in esp32_devices.items():
        last_seen = info.get("last_seen", 0)
        if now - last_seen > 120:
            status = "offline"
        else:
            status = "online"
        
        devices_by_status[status].append({
            "device_id": device_id,
            "location": info.get("location"),
            "ip_address": info.get("ip_address"),
            "last_seen": last_seen,
            "total_triggers": info.get("total_triggers", 0)
        })
    
    return jsonify({
        "total_devices": len(esp32_devices),
        "online_count": len(devices_by_status["online"]),
        "offline_count": len(devices_by_status["offline"]),
        "devices_online": devices_by_status["online"],
        "devices_offline": devices_by_status["offline"]
    })


# ============================================================
# Legacy Serial Reader Support (for Arduino via USB)
# ============================================================

@app.route("/serial/connect", methods=["POST"])
def serial_connect():
    """
    Simulate serial connection status.
    (Used for legacy Arduino integration)
    """
    data = request.get_json(silent=True) or {}
    port = data.get("port", "unknown")
    
    logger.info("Serial connection: port=%s", port)
    
    return jsonify({
        "status": "connected",
        "port": port,
        "device": "arduino_uno",
        "message": "Serial connection established"
    })


@app.route("/serial/disconnect", methods=["POST"])
def serial_disconnect():
    """Simulate serial disconnection"""
    logger.info("Serial disconnected")
    
    return jsonify({
        "status": "disconnected",
        "message": "Serial connection closed"
    })


if __name__ == "__main__":
    logger.info("Smart Evacuation backend listening at http://localhost:5000")
    logger.info("Emergency timeout is %s seconds (0 disables auto-clear)", EMERGENCY_TIMEOUT_SECONDS)
    logger.info("ESP32 WiFi mode: enabled (devices can connect via HTTP)")
    app.run(debug=True, host="0.0.0.0", port=5000)
