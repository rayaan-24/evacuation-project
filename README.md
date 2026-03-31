# 🚨 Smart Emergency Evacuation Path Finder
## Using Ant Colony Optimization (ACO) + ESP32 WiFi Integration

---

## 🎯 Overview

This project creates a **Smart Emergency Evacuation System** that uses **Ant Colony Optimization (ACO)** to find the safest evacuation routes in a building. It features **ESP32 microcontrollers** with **WiFi connectivity** to detect and respond to emergencies in real-time.

### Key Features

✅ **30-Button Emergency Matrix** - Manual corridor blocking  
✅ **WiFi Connectivity** - No USB cables to ESP32  
✅ **Real-time Updates** - Instant frontend updates  
✅ **ACO Pathfinding** - AI-powered route optimization  
✅ **Multi-Emergency** - Handles multiple simultaneous hazards  
✅ **Web Dashboard** - Visual map with live status  

---

## 📁 Project Structure

```
project4/
├── esp32/                      # ESP32 Firmware
│   └── firmware/
│       └── esp32_emergency_controller/
│           ├── esp32_emergency_controller.ino
│           ├── config.h
│           └── README.md
├── backend/                    # Flask API Server
│   ├── app.py                # Main Flask application
│   ├── aco.py               # Ant Colony Optimization
│   ├── pathfinder.py        # Path calculation
│   ├── simulation.py        # Evacuation simulation
│   └── serial_reader.py     # Legacy Arduino support
├── frontend/                 # Web Interface
│   ├── smart_evacuation_demo.html
│   ├── sensor_overlay.js
│   ├── iot_control_panel.html
│   ├── renderer.js
│   └── interactivity.js
├── data/                      # Building Data
│   └── building_layout.json
├── docs/                      # Documentation
│   ├── ESP32_INTEGRATION.md
│   ├── HARDWARE_SETUP.md
│   └── TESTING_CHECKLIST.md
└── README.md
```

---

## 🧠 How It Works

### Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                    ESP32 SMART EVACUATION SYSTEM              │
├──────────────────────────────────────────────────────────────┤
│                                                               │
│  [ESP32 Button Matrix] ──WiFi──→ [Flask API Server]        │
│   (30 Emergency Buttons)              (Port 5000)            │
│                                              │               │
│                                              ↓               │
│                                       [ACO Algorithm]        │
│                                       (Pathfinding)          │
│                                              │               │
│                                              ↓               │
│                                       [Web Dashboard]       │
│                                       (Real-time UI)        │
│                                                               │
└──────────────────────────────────────────────────────────────┘
```

### Step-by-Step Flow

1. **Button Press** - User presses button on ESP32 matrix
2. **ESP32 Processing** - Detects button, determines corridor & emergency type
3. **WiFi Transmission** - Sends HTTP POST to Flask API
4. **Backend Processing** - Stores emergency, updates status
5. **Path Recalculation** - ACO algorithm finds safe route
6. **Frontend Update** - Map and status update in browser

---

## 🚀 Quick Start

### Prerequisites

1. **Python 3.7+**
2. **Arduino IDE** (for ESP32 programming)
3. **ESP32 DevKit v1**
4. **30 Tactile Buttons**
5. **WiFi Network**

### Step 1: Install Python Dependencies

```bash
cd backend
pip install flask flask-cors pyserial requests
```

### Step 2: Configure ESP32

**File:** `esp32/firmware/esp32_emergency_controller/config.h`

Edit these values:
```cpp
#define WIFI_SSID "YourWiFiName"
#define WIFI_PASSWORD "YourWiFiPassword"
#define API_HOST "http://192.168.1.100:5000"
```

### Step 3: Wire ESP32

See `esp32/firmware/esp32_emergency_controller/README.md` for wiring diagram.

**Quick Reference:**
```
GPIO 4-8   → Button Rows (5 rows)
GPIO 9-14  → Button Columns (6 columns)
GPIO 15-17 → Status LEDs
GPIO 18    → Buzzer
GND        → All buttons (common ground)
```

### Step 4: Upload ESP32 Firmware

1. Open `esp32_emergency_controller.ino` in Arduino IDE
2. Select: **Tools → Board → ESP32 Arduino → ESP32 Dev Module**
3. Select your COM port
4. Upload (Ctrl+U)

### Step 5: Start Flask Backend

**Terminal 1:**
```bash
cd backend
python app.py
```

You should see:
```
Smart Evacuation backend listening at http://localhost:5000
ESP32 WiFi mode: enabled
```

### Step 6: Open Frontend

Open browser to: **http://localhost:5000/**

### Step 7: Test!

Press buttons on ESP32 matrix:
- Watch Serial Monitor (115200 baud)
- See emergency appear on frontend
- Run evacuation to see path calculation

---

## 🔌 ESP32 Wiring

### Button Matrix (30 buttons)

```
ESP32 GPIO 4  ──→ Row 0 buttons (0, 1, 2, 3, 4, 5)
ESP32 GPIO 5  ──→ Row 1 buttons (6, 7, 8, 9, 10, 11)
ESP32 GPIO 6  ──→ Row 2 buttons (12, 13, 14, 15, 16, 17)
ESP32 GPIO 7  ──→ Row 3 buttons (18, 19, 20, 21, 22, 23)
ESP32 GPIO 8  ──→ Row 4 buttons (24, 25, 26, 27, 28, 29)

ESP32 GPIO 9  ──→ Column 0 (buttons 0, 6, 12, 18, 24)
ESP32 GPIO 10 ──→ Column 1 (buttons 1, 7, 13, 19, 25)
ESP32 GPIO 11 ──→ Column 2 (buttons 2, 8, 14, 20, 26)
ESP32 GPIO 12 ──→ Column 3 (buttons 3, 9, 15, 21, 27)
ESP32 GPIO 13 ──→ Column 4 (buttons 4, 10, 16, 22, 28)
ESP32 GPIO 14 ──→ Column 5 (buttons 5, 11, 17, 23, 29)

ESP32 GND ──────→ All buttons (common ground)
```

### Status Indicators

```
ESP32 GPIO 2  ──→ Built-in LED (WiFi status)
ESP32 GPIO 15 ──→ 220Ω ──→ Red LED (+) ──→ GND
ESP32 GPIO 16 ──→ 220Ω ──→ Yellow LED (+) ──→ GND
ESP32 GPIO 17 ──→ 220Ω ──→ Green LED (+) ──→ GND
```

### Buzzer

```
ESP32 GPIO 18 ──→ Buzzer (+) ──→ GND
```

---

## 🕹️ How to Use

### Emergency Types (Cycle on Each Button Press)

| Press # | Type | Color | Description |
|---------|------|-------|-------------|
| 1 | FIRE | Red | Fire emergency |
| 2 | SMOKE | Orange | Smoke detected |
| 3 | GAS | Purple | Gas leak |
| 4 | BLOCKAGE | Blue | Path blocked |
| 5 | CROWD | Yellow | High density |
| 6 | (cycles) | - | Returns to FIRE |

### Running Evacuation

1. **Select Start Room** - Choose where you're evacuating from
2. **Block Corridors** - Press buttons on ESP32 to mark hazards
3. **Click "RUN EVACUATION"** - System calculates safest route
4. **Follow Path** - Animated route shows safest way out

---

## 📡 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Frontend dashboard |
| `/api` | GET | API information |
| `/layout` | GET | Building layout data |
| `/find-path` | POST | Calculate evacuation route |
| `/sensor-update` | POST | ESP32 sends emergency |
| `/sensor-status` | GET | Get active emergencies |
| `/esp32/register` | POST | ESP32 registration |
| `/esp32/heartbeat` | POST | ESP32 status check |
| `/esp32/devices` | GET | List ESP32 devices |
| `/reset-emergencies` | POST | Clear all emergencies |

---

## 📊 Testing

### Manual Testing (No ESP32)

Use the IoT Control Panel: **http://localhost:5000/iot_control_panel.html**

Click sensor buttons directly to test the system.

### ESP32 Testing

1. Connect ESP32 to WiFi
2. Check Serial Monitor (115200 baud)
3. Press buttons
4. Watch Serial output and frontend

### Complete Flow Testing

1. Press 3 buttons on ESP32 (blocks 3 corridors)
2. Select start room on frontend
3. Click "RUN EVACUATION"
4. Verify path avoids blocked corridors
5. Block additional corridor
6. Path should recalculate

---

## 🎓 For Viva/Exam

**Q: Why use ESP32 instead of Arduino?**
A: ESP32 has built-in WiFi, eliminating USB cables. It can send data directly to the server over HTTP, enabling wireless deployment. Multiple ESP32s can connect to the same server for scalable systems.

**Q: How does the button matrix work?**
A: A 5×6 matrix uses 11 GPIO pins to control 30 buttons. We scan each row (set one LOW) and read columns (detect which are pulled LOW). This is called multiplexed input.

**Q: How does the ACO algorithm work?**
A: We simulate "digital ants" that walk through the building graph. Ants prefer paths with stronger "pheromone trails" (higher safety ratings). Fire zones have low pheromone, so ants find alternative routes.

**Q: Why cycle emergency types on each press?**
A: To allow flexible marking. One button can mark a corridor as FIRE, then SMOKE, then CLEAR (by cycling through), etc.

---

## 💰 Cost Estimate

| Component | Quantity | Cost |
|-----------|----------|------|
| ESP32 DevKit v1 | 1 | $8-12 |
| Breadboard | 1 | $5-7 |
| 30 Buttons | 1 pack | $3-4 |
| Jumper Wires | 1 pack | $4-5 |
| LEDs + Resistors | - | $1 |
| Buzzer | 1 | $1-2 |
| **Total** | | **$22-31** |

---

## 📚 Documentation

- **[ESP32 Integration Guide](docs/ESP32_INTEGRATION.md)** - Complete ESP32 setup
- **[ESP32 Firmware README](esp32/firmware/esp32_emergency_controller/README.md)** - Firmware details
- **[Testing Checklist](docs/TESTING_CHECKLIST.md)** - Verification procedures
- **[Hardware Setup](docs/HARDWARE_SETUP.md)** - Detailed wiring

---

## 🆘 Troubleshooting

### ESP32 won't connect to WiFi
1. Verify SSID and password
2. Check WiFi is 2.4GHz
3. Move ESP32 closer to router

### Backend won't receive events
1. Ensure Flask is running
2. Check firewall allows port 5000
3. Verify API_HOST IP is correct

### Frontend not updating
1. Refresh browser (Ctrl+F5)
2. Check browser console (F12)
3. Verify API responding: `curl http://localhost:5000/api`

---

## 🎯 Project Status

- ✅ Backend API complete
- ✅ Frontend dashboard complete
- ✅ ESP32 firmware complete
- ✅ WiFi integration working
- ✅ Real-time updates functional
- ✅ ACO algorithm integrated
- ✅ Documentation complete

**Ready for deployment!** 🚀

---

## 👨‍💻 Tech Stack

| Layer | Technology |
|-------|------------|
| Hardware | ESP32 DevKit v1 |
| Connectivity | WiFi (802.11 b/g/n) |
| Backend | Python, Flask, Flask-CORS |
| Algorithm | Ant Colony Optimization |
| Frontend | HTML5, CSS3, JavaScript (Canvas API) |
| Data Format | JSON REST API |

---

## 📞 Support

For issues:
1. Check Serial Monitor output
2. Review Flask backend logs
3. Consult documentation files
4. Test components individually

---

## 📄 License

This is an academic project for demonstration purposes.

---

**Built with ❤️ for Smart Building Safety**
