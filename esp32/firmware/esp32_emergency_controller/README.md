# ESP32 Smart Evacuation Controller

## Quick Start

### Hardware Requirements

| Component | Quantity | Purpose |
|-----------|----------|---------|
| ESP32 DevKit v1 | 1 | Main controller |
| Breadboard | 1 | Prototyping |
| Tactile Buttons (6×6mm) | 30 | Emergency triggers |
| Jumper Wires | 40+ | Connections |
| LEDs (Red, Yellow, Green) | 3 | Status indicators |
| 220Ω Resistors | 3 | LED current limiting |
| Active Buzzer (5V) | 1 | Audio alerts |
| USB Cable | 1 | Power + Programming |
| 5V/2A Power Adapter | 1 | Stable power (optional) |

**Total Cost: ~$25-35**

### Software Requirements

1. **Arduino IDE** (v1.8+)
   - Download: https://www.arduino.cc/en/software

2. **ESP32 Board Support**
   - Add URL: `https://dl.espressif.com/dl/package_esp32_index.json`
   - Install: "ESP32 by Espressif Systems"

3. **Required Libraries**
   - `ArduinoJson` (v6+) - Install via Library Manager

---

## Setup Instructions

### Step 1: Install Arduino IDE + ESP32 Support

1. Download and install Arduino IDE
2. Open Arduino IDE
3. Go to: **File → Preferences**
4. In "Additional Board Manager URLs", add:
   ```
   https://dl.espressif.com/dl/package_esp32_index.json
   ```
5. Click OK
6. Go to: **Tools → Board → Board Manager**
7. Search for "ESP32"
8. Install: **esp32 by Espressif Systems**

### Step 2: Install Required Libraries

1. Go to: **Sketch → Include Library → Manage Libraries**
2. Search for "ArduinoJson"
3. Install: **ArduinoJson by Benoit Blanchon** (v6+)

### Step 3: Configure WiFi & Network

**File:** `config.h`

Edit these values:

```cpp
// Your WiFi Network
#define WIFI_SSID "YourWiFiName"
#define WIFI_PASSWORD "YourWiFiPassword"

// Your PC's IP address (see Finding Your PC IP below)
#define API_HOST "http://192.168.1.100:5000"
```

**Finding Your PC IP:**

**Windows:**
```
1. Press Win + R
2. Type: cmd
3. Press Enter
4. Type: ipconfig
5. Look for "IPv4 Address" under WiFi
   Example: 192.168.1.100
```

**Mac/Linux:**
```bash
# Open Terminal
# Type:
ifconfig | grep "inet "
# Look for WiFi interface
# Example: 192.168.1.100
```

### Step 4: Wire the Hardware

**Button Matrix (30 buttons):**

```
ESP32 GPIO 4  ──→ Row 0 (buttons 0, 1, 2, 3, 4, 5)
ESP32 GPIO 5  ──→ Row 1 (buttons 6, 7, 8, 9, 10, 11)
ESP32 GPIO 6  ──→ Row 2 (buttons 12, 13, 14, 15, 16, 17)
ESP32 GPIO 7  ──→ Row 3 (buttons 18, 19, 20, 21, 22, 23)
ESP32 GPIO 8  ──→ Row 4 (buttons 24, 25, 26, 27, 28, 29)

ESP32 GPIO 9  ──→ Column 0 (buttons 0, 6, 12, 18, 24)
ESP32 GPIO 10 ──→ Column 1 (buttons 1, 7, 13, 19, 25)
ESP32 GPIO 11 ──→ Column 2 (buttons 2, 8, 14, 20, 26)
ESP32 GPIO 12 ──→ Column 3 (buttons 3, 9, 15, 21, 27)
ESP32 GPIO 13 ──→ Column 4 (buttons 4, 10, 16, 22, 28)
ESP32 GPIO 14 ──→ Column 5 (buttons 5, 11, 17, 23, 29)

ESP32 GND ──────→ All buttons (common ground)
```

**Status LEDs:**

```
ESP32 GPIO 15 ──→ 220Ω ──→ Red LED (+) ──→ GND
ESP32 GPIO 16 ──→ 220Ω ──→ Yellow LED (+) ──→ GND
ESP32 GPIO 17 ──→ 220Ω ──→ Green LED (+) ──→ GND
```

**Buzzer:**

```
ESP32 GPIO 18 ──→ Buzzer (+) ──→ GND
```

**Built-in LED:**

```
ESP32 GPIO 2 ──→ Built-in LED (WiFi status)
```

### Step 5: Upload Firmware

1. Open `esp32_emergency_controller.ino` in Arduino IDE
2. Connect ESP32 via USB
3. Select Board: **Tools → Board → ESP32 Arduino → ESP32 Dev Module**
4. Select Port: **Tools → Port → COMX** (where X is your port)
5. Click Upload (Ctrl+U or arrow button)
6. Wait for "Done uploading"

### Step 6: Monitor Serial Output

1. Open Serial Monitor: **Tools → Serial Monitor**
2. Set baud rate: **115200**
3. You should see:
   ```
   ╔════════════════════════════════════════════════════╗
   ║   ESP32 SMART EVACUATION CONTROLLER               ║
   ║   30-Button Emergency Matrix + WiFi               ║
   ╚════════════════════════════════════════════════════╝
   
   Connecting to WiFi...
   ✓ WiFi Connected!
   IP Address: 192.168.1.101
   ✓ System Ready!
   ```

### Step 7: Start Backend

**Terminal 1:**
```bash
cd backend
python app.py
```

### Step 8: Test!

Press any button on the matrix:
- Serial Monitor shows: `🔴 EMERGENCY TRIGGERED! Button 0 (C1A-North) → sensor_0 → FIRE`
- Flask backend receives the event
- Frontend updates in real-time

---

## How It Works

### Button → Emergency Flow

```
[Button Press]
     ↓
[ESP32 Matrix Scan]
     ↓
[Determine Button Index (0-29)]
     ↓
[Cycle Emergency Type (FIRE→SMOKE→GAS→BLOCKAGE→CROWD)]
     ↓
[Send HTTP POST to Flask API]
     ↓
[Flask stores emergency]
     ↓
[Frontend polls and updates]
```

### Emergency Types (Cycles on Each Press)

| Press # | Type | Color | Description |
|---------|------|-------|-------------|
| 1 | FIRE | Red | Fire/fire hazard |
| 2 | SMOKE | Orange | Smoke detection |
| 3 | GAS | Purple | Gas leak |
| 4 | BLOCKAGE | Blue | Physical obstruction |
| 5 | CROWD | Yellow | Crowd density |
| 6 | FIRE | Red | (Cycles back) |

### Status LEDs

| LED | Color | Meaning |
|-----|-------|---------|
| Built-in (GPIO 2) | Blue | WiFi connected |
| GPIO 15 | Red | Emergency active |
| GPIO 16 | Yellow | Warning/system issue |
| GPIO 17 | Green | System ready |

### Serial Monitor Messages

```
🔴 EMERGENCY TRIGGERED!
   Button: 0 (C1A-North)
   Sensor: sensor_0
   Type:   FIRE

📡 Sending emergency to server...
✓ Emergency sent! (took 123 ms)
```

---

## Troubleshooting

### Issue: "WiFi Connection Failed"

**Solutions:**
1. Check WiFi SSID and password in config.h
2. Ensure WiFi is 2.4GHz (ESP32 doesn't support 5GHz)
3. Move ESP32 closer to router
4. Check if router has MAC filtering

### Issue: "Failed to send: connection refused"

**Solutions:**
1. Ensure Flask backend is running on PC
2. Check PC's firewall allows port 5000
3. Verify API_HOST IP address is correct
4. Ensure PC and ESP32 on same network

### Issue: Buttons not responding

**Solutions:**
1. Check wiring connections
2. Ensure all buttons connected to GND
3. Verify row/column pins correct
4. Press button longer (debounce might be filtering)

### Issue: ESP32 not detected

**Solutions:**
1. Press BOOT button on ESP32 while uploading
2. Try different USB cable (needs data capability)
3. Install CH340 USB driver (for some ESP32 boards)
4. Select correct board in Tools menu

### Issue: Serial Monitor shows garbage

**Solutions:**
1. Set baud rate to 115200 (not 9600)
2. Click "Carriage Return" or "Both NL & CR"
3. Reset ESP32 (press EN button)

---

## Advanced Configuration

### Multiple ESP32 Devices

For large buildings, use multiple ESP32s:

```cpp
// ESP32 #1 (Floor 1)
#define DEVICE_ID "ESP32-F1-001"
#define DEVICE_LOCATION "Floor 1 - North Wing"

// ESP32 #2 (Floor 2)
#define DEVICE_ID "ESP32-F2-001"
#define DEVICE_LOCATION "Floor 2 - South Wing"
```

Sensor IDs automatically include device prefix:
- `sensor_0` becomes `sensor_0` (from ESP32-F1-001)

### Static IP Configuration

```cpp
// Add to setup()
IPAddress localIP(192, 168, 1, 101);  // Desired IP
IPAddress gateway(192, 168, 1, 1);   // Router IP
IPAddress subnet(255, 255, 255, 0);   // Subnet mask

WiFi.config(localIP, gateway, subnet);
WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
```

### Adjusting Button Behavior

```cpp
// In esp32_emergency_controller.ino

const unsigned long DEBOUNCE_MS = 50;      // Increase if noisy
const unsigned long REPEAT_BLOCK_MS = 1000; // Prevent rapid repeats
```

### Custom Button Labels

Edit in `esp32_emergency_controller.ino`:

```cpp
const char* BUTTON_LABELS[TOTAL_BUTTONS] = {
  "Main Entrance", "Corridor A", "Exit North",
  // ... customize labels
};
```

---

## Testing Without Flask Backend

For standalone testing, modify the code to print instead of send:

```cpp
// In handleButtonPress(), replace sendEmergencyToAPI() with:
Serial.printf("EMERGENCY: %s, %s\n", sensorId, emergencyType);
```

---

## Performance Specifications

| Metric | Value |
|--------|-------|
| Button scan rate | 100 times/sec |
| Debounce time | 50ms |
| HTTP response timeout | 5 seconds |
| WiFi reconnect attempts | 3 |
| Heartbeat interval | 60 seconds |
| Power consumption | ~240mA (WiFi on) |

---

## Support

For issues:
1. Check Serial Monitor for error messages
2. Verify all wiring connections
3. Ensure WiFi credentials correct
4. Check Flask backend is running
5. Consult Troubleshooting section above

---

## Version History

- **v1.0** (Current)
  - Initial release
  - 30-button matrix
  - WiFi connectivity
  - HTTP API integration
  - Status LEDs + buzzer

---

**Status: Ready for Deployment** ✅
