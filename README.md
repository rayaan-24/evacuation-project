# 🚨 Smart Emergency Evacuation Path Finder
## Using Ant Colony Optimization (ACO) + IoT Integration

---

## 📁 Project Structure

```
/project
  /frontend
    index.html        → Main webpage (the visual UI)
    style.css         → All styling (dark tactical theme)
    script.js         → Frontend logic (talks to backend)
    canvas_map.js     → Draws the floor plan on canvas
  /backend
    app.py            → Flask API server (main backend)
    aco.py            → Ant Colony Optimization algorithm
    pathfinder.py     → Converts map to graph + generates directions
    serial_reader.py  → Reads Arduino via USB, sends to Flask
  /iot
    arduino_code.ino  → Upload this to Arduino Uno
  /data
    building_layout.json → Floor plan data (rooms, corridors, exits)
  README.md
```

---

## 🧠 How It Works (Simple Explanation)

Imagine you're inside a building that's on fire. How do you escape?

1. **IoT Sensors (Arduino)** detect smoke/fire in rooms
2. **Python (serial_reader.py)** reads that data from USB
3. **Flask API (app.py)** receives the fire location
4. **ACO Algorithm (aco.py)** sends hundreds of "digital ants" through the building map
5. **Ants follow pheromone trails** — shorter, safer paths get stronger trails
6. **Best path is found** and sent to the frontend
7. **Canvas map** draws the green path with step-by-step directions

---

## 🚀 How to Run (Step by Step)

### Step 1: Install Python packages

```bash
pip install flask flask-cors pyserial requests
```

### Step 2: Start the Flask Backend

```bash
cd project/backend
python app.py
```

You should see:
```
🚀 Smart Evacuation System Backend
   Running at http://localhost:5000
```

### Step 3: Open the Frontend

Option A — Just open the file:
```
Double-click: project/frontend/index.html
```

Option B — Use a local server (better):
```bash
cd project/frontend
python -m http.server 8000
# Then open: http://localhost:8000
```

### Step 4: Connect Arduino (Optional)

1. Wire sensors (see wiring below)
2. Upload `iot/arduino_code.ino` to Arduino
3. Note the COM port (e.g., COM3 on Windows, /dev/ttyUSB0 on Linux)
4. Edit `backend/serial_reader.py` — change `SERIAL_PORT`
5. Run:
```bash
python serial_reader.py
```

### Step 5: Test Without Arduino

```bash
python serial_reader.py demo
```

Or click **"🔥 Trigger Fire"** buttons in the web UI!

---

## 🔌 Arduino Wiring

```
Arduino Uno
│
├── A0 ──────────── MQ-2 Smoke Sensor (A0/analog pin)
├── D2 ──────────── Flame Sensor (D0/digital pin)
├── D13 ─────────── Red LED (+) → 220Ω resistor → GND
├── 5V ──────────── MQ-2 VCC + Flame VCC
└── GND ─────────── MQ-2 GND + Flame GND + LED (-)
```

**MQ-2 Smoke Sensor:**
- VCC → 5V
- GND → GND
- A0 → Arduino A0

**Flame Sensor (IR):**
- VCC → 5V
- GND → GND
- D0 → Arduino D2

---

## 🏢 Building Layout

The map represents **VIT Tech Block — Floor 2** with:

| Room         | Size (m)  | Capacity |
|--------------|-----------|----------|
| Lab 201      | 16m × 12m | 40       |
| Lab 202      | 16m × 12m | 40       |
| Lecture 203  | 16m × 12m | 60       |
| Staff Room   | 16m × 12m | 15       |
| Lab 204      | 16m × 12m | 40       |
| Seminar Hall | 20m × 12m | 80       |
| Server Room  | 12m × 12m | 5        |
| Store Room   | 16m × 12m | 5        |

**Special Zones:**
- 🪜 Staircase A & B — Emergency exits (preferred)
- 🛗 Lift — Disabled during fire
- 🚪 Exit A (left) & Exit B (right) — Final evacuation points

---

## 🐜 ACO Algorithm Explained

**Ant Colony Optimization** mimics real ants finding food:

1. **Many ants** start from your room
2. Each ant walks **randomly** but **prefers shorter, safer paths**
3. Ants on shorter paths reach the exit faster
4. They leave more **pheromone** (smell) on their path
5. Future ants **follow strong pheromone trails**
6. Over 100 iterations, **best path emerges**

**Parameters:**
- `alpha = 1.0` → How much pheromone matters
- `beta = 3.0` → How much distance matters (higher = prefer shorter)
- `evaporation = 0.5` → How fast pheromone fades
- `danger_penalty = 10x` → Fire zones are 10× harder to go through

---

## 🔥 Fire Scenarios (Testing)

| Scenario | Start | Fire | Expected Exit |
|----------|-------|------|---------------|
| Left side fire  | R4 | R1, R2 | Exit B |
| Right side fire | R1 | R3, R4 | Exit A |
| Center fire     | R1 | R6     | Exit A |
| Multiple fires  | R7 | R6, R8 | Exit A or B (ACO decides) |

---

## 📡 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Welcome message |
| `/layout` | GET | Get building JSON |
| `/find-path` | POST | Run ACO pathfinding |
| `/sensor-update` | POST | Arduino sends data here |
| `/sensor-status` | GET | Get current fire locations |
| `/simulate-sensor` | POST | Test without Arduino |

**Example POST to /find-path:**
```json
{
  "start_room": "R3",
  "fire_rooms": ["R2"],
  "emergency_type": "fire"
}
```

**Example Response:**
```json
{
  "success": true,
  "best_exit": "E2",
  "total_distance_m": 42.5,
  "total_steps": 5,
  "directions": [
    {"step": 1, "instruction": "🚶 Walk 12.0m South (↓) → Corridor W3 Entry"}
  ]
}
```

---

## 🧪 Running Tests

```bash
cd project/backend

# Test ACO directly
python aco.py

# Test pathfinder
python pathfinder.py

# Test IoT simulation
python serial_reader.py demo
```

---

## 🎓 For Viva/Exam

**Q: Why use ACO instead of Dijkstra?**
A: Dijkstra finds one shortest path. ACO finds the safest path by adding danger penalties for fire zones, which Dijkstra cannot do easily. ACO also handles dynamic fire spread better.

**Q: How does the distance system work?**
A: 1 pixel = 0.1 meters. A room of width 160px = 16 meters. All distances are calculated using the Euclidean formula: √((x2-x1)² + (y2-y1)²) × 0.1

**Q: How do IoT sensors connect to the map?**
A: The `sensor_map` in building_layout.json maps sensor IDs to room IDs. When sensor_1 detects fire, it automatically marks Room R1 as a danger zone.

**Q: Why is the lift disabled during fire?**
A: Lifts can fail during fire (power cuts, smoke fills shaft). Staircases are always preferred in emergency evacuations (building codes require this).

---

## 👨‍💻 Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | HTML5, CSS3, JavaScript (Canvas API) |
| Backend | Python, Flask, Flask-CORS |
| Algorithm | Ant Colony Optimization (custom implementation) |
| IoT | Arduino Uno, MQ-2 Sensor, Flame Sensor |
| Communication | USB Serial → Python → HTTP/REST API |
| Data Format | JSON |
