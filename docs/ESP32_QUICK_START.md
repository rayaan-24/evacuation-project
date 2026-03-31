# ESP32 Quick Start Guide

## Get Started in 5 Minutes

### Step 1: Install Software (2 min)

1. **Arduino IDE**
   - Download: https://www.arduino.cc/en/software
   - Install and open

2. **Add ESP32 Board Support**
   - File → Preferences
   - Add to "Additional Board Manager URLs":
     ```
     https://dl.espressif.com/dl/package_esp32_index.json
     ```
   - Tools → Board → Board Manager
   - Install "ESP32 by Espressif Systems"

3. **Install Library**
   - Sketch → Include Library → Manage Libraries
   - Install "ArduinoJson by Benoit Blanchon"

### Step 2: Configure WiFi (1 min)

**File:** `esp32/firmware/esp32_emergency_controller/config.h`

```cpp
#define WIFI_SSID "YourWiFiName"
#define WIFI_PASSWORD "YourWiFiPassword"
#define API_HOST "http://192.168.1.100:5000"
```

**Find your PC IP:**
- Windows: `ipconfig` → IPv4 Address
- Mac/Linux: `ifconfig` → inet

### Step 3: Wire Hardware (2 min)

**Button Matrix (30 buttons):**
```
GPIO 4,5,6,7,8 ──→ Row pins (5 rows)
GPIO 9,10,11,12,13,14 ──→ Column pins (6 columns)
GND ──→ All buttons
```

**Status LEDs:**
```
GPIO 15 ──→ Red LED ──→ 220Ω ──→ GND
GPIO 16 ──→ Yellow LED ──→ 220Ω ──→ GND
GPIO 17 ──→ Green LED ──→ 220Ω ──→ GND
```

**Buzzer:**
```
GPIO 18 ──→ Buzzer ──→ GND
```

### Step 4: Upload Firmware (30 sec)

1. Open `esp32_emergency_controller.ino`
2. Tools → Board → ESP32 Dev Module
3. Tools → Port → COMX
4. Upload (Ctrl+U)

### Step 5: Start Backend (30 sec)

```bash
cd backend
python app.py
```

### Step 6: Open Frontend

Browser: http://localhost:5000/

---

## First Test

1. Press button on ESP32 matrix
2. Watch Serial Monitor (115200 baud)
3. See emergency on frontend
4. Run evacuation

**Success!** ✅

---

## Common Issues

### "WiFi Connection Failed"
- Check SSID/password in config.h
- Ensure WiFi is 2.4GHz

### "Failed to send"
- Verify Flask running
- Check PC firewall
- Confirm API_HOST IP correct

### "Board not detected"
- Install CH340 driver
- Try different USB cable
- Press BOOT button during upload

---

## Need Help?

See full documentation:
- `docs/ESP32_INTEGRATION.md`
- `esp32/firmware/esp32_emergency_controller/README.md`
