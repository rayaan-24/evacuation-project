# ESP32 Integration Guide

## Overview

The Smart Evacuation System now supports **ESP32 microcontrollers** via WiFi connectivity. This replaces the previous Arduino-based serial communication with a more flexible, wireless solution.

## Architecture Comparison

### Arduino (Legacy)
```
Arduino → USB Cable → Serial Reader → Flask API → Frontend
         (Physical cable required)
```

### ESP32 (New)
```
ESP32 → WiFi → Flask API → Frontend
       (Wireless! No USB data cable needed)
```

## Benefits of ESP32

| Feature | Arduino | ESP32 | Advantage |
|---------|---------|-------|-----------|
| Connectivity | USB Serial only | WiFi + Bluetooth + USB | Multiple options |
| Range | Limited by USB cable | WiFi range | Place anywhere |
| Cables | USB cable required | Power only (optional) | Cleaner setup |
| Scalability | 1 device | Multiple devices | Expandable system |
| Power | USB only | USB, adapter, battery | Flexible power |
| Cost | $8-10 | $8-15 | Similar price |

## Quick Setup

### 1. Configure WiFi

**File:** `esp32/firmware/esp32_emergency_controller/config.h`

```cpp
#define WIFI_SSID "YourWiFiName"
#define WIFI_PASSWORD "YourWiFiPassword"
#define API_HOST "http://192.168.1.100:5000"
```

### 2. Upload Firmware

1. Open `esp32_emergency_controller.ino` in Arduino IDE
2. Select: Tools → Board → ESP32 Arduino → **ESP32 Dev Module**
3. Select Port: COMX (your ESP32 port)
4. Upload (Ctrl+U)

### 3. Start Backend

```bash
cd backend
python app.py
```

### 4. Test

Press buttons on ESP32 matrix → Watch frontend update!

---

## How ESP32 Communication Works

### Connection Flow

```
ESP32 Boot
    ↓
Connect to WiFi
    ↓
Register with Flask (/esp32/register)
    ↓
Send heartbeats (/esp32/heartbeat)
    ↓
On button press → Send emergency (/sensor-update)
```

### Message Format

**Emergency Trigger:**
```json
{
  "sensor_id": "sensor_0",
  "type": "FIRE",
  "device_id": "ESP32-001",
  "source": "esp32_button"
}
```

**Registration:**
```json
{
  "device_id": "ESP32-001",
  "location": "Floor 1 - North Wing",
  "ip_address": "192.168.1.101",
  "wifi_ssid": "MyWiFi",
  "button_count": 30,
  "firmware_version": "1.0"
}
```

**Heartbeat:**
```json
{
  "device_id": "ESP32-001",
  "rssi": -45,
  "uptime_ms": 3600000,
  "total_triggers": 150
}
```

---

## ESP32 API Endpoints

### 1. Register Device
```
POST /esp32/register
```

Called when ESP32 boots up. Registers the device with the server.

**Response:**
```json
{
  "status": "registered",
  "device_id": "ESP32-001",
  "message": "Device registered successfully",
  "server_time": 1743400000.123
}
```

### 2. Heartbeat
```
POST /esp32/heartbeat
```

Periodic check-in (every 60 seconds) to show device is alive.

**Response:**
```json
{
  "status": "ok",
  "device_id": "ESP32-001",
  "server_time": 1743400000.123
}
```

### 3. List Devices
```
GET /esp32/devices
```

Get all registered ESP32 devices.

**Response:**
```json
{
  "devices": [...],
  "total": 2,
  "online": 2,
  "offline": 0
}
```

### 4. Device Status
```
GET /esp32/status
```

Get detailed status of all ESP32 devices.

### 5. Sensor Update
```
POST /sensor-update
```

**Same as before** - ESP32 sends emergency events here.

---

## Multiple ESP32 Devices

For larger buildings, deploy multiple ESP32s:

### Configuration Example

**ESP32 #1 (Floor 1):**
```cpp
#define DEVICE_ID "ESP32-F1-001"
#define DEVICE_LOCATION "Floor 1 - North Wing"
```

**ESP32 #2 (Floor 2):**
```cpp
#define DEVICE_ID "ESP32-F2-001"
#define DEVICE_LOCATION "Floor 2 - South Wing"
```

### Sensor ID Strategy

**Option A: Separate ID ranges**
- ESP32 #1: sensor_0 to sensor_29
- ESP32 #2: sensor_30 to sensor_59

**Option B: Prefixed IDs**
- ESP32 #1: f1_sensor_0, f1_sensor_1, ...
- ESP32 #2: f2_sensor_0, f2_sensor_1, ...

**Option C: Location-based**
- ESP32 #1: F1_C1A, F1_C2A, ...
- ESP32 #2: F2_C1A, F2_C2A, ...

---

## WiFi Network Requirements

### For Testing (Home/Office)
- Standard home WiFi router
- 2.4GHz network (ESP32 doesn't support 5GHz)
- PC and ESP32 on same network
- No special configuration needed

### For Demonstration
- Dedicated WiFi network (optional)
- Or use ESP32 as WiFi hotspot (limited range)
- Ensure firewall allows port 5000

### For Production
- Enterprise WiFi with WPA2-Enterprise (advanced)
- Or wired Ethernet + WiFi bridge
- Static IP assignment (recommended)

---

## Power Options

### Development
```
USB Cable → Computer
- Convenient
- Powers ESP32 (5V, ~240mA)
- Data connection for debugging
```

### Standalone
```
5V/2A Power Adapter → ESP32 Vin
- Stable power
- No USB cable needed
- Clean installation
```

### Battery Backup
```
LiPo Battery (3.7V) → LDO Regulator (3.3V) → ESP32
- Uninterruptible power
- Portable
- For critical systems
```

---

## Troubleshooting

### Issue: ESP32 won't connect to WiFi

**Symptoms:** Serial shows "WiFi Connection Failed"

**Solutions:**
1. Verify SSID and password in config.h
2. Ensure WiFi is 2.4GHz (not 5GHz)
3. Check WiFi is working (connect phone/laptop)
4. Move ESP32 closer to router
5. Check router has no MAC filtering

### Issue: Backend won't receive events

**Symptoms:** ESP32 sends but Flask doesn't show events

**Solutions:**
1. Check ESP32 Serial Monitor for HTTP errors
2. Verify Flask backend is running
3. Check PC's firewall allows port 5000
4. Ensure API_HOST IP is correct
5. Ping ESP32 from PC: `ping 192.168.1.101`

### Issue: Events delayed or lost

**Symptoms:** Button press takes long to appear on frontend

**Solutions:**
1. Check WiFi signal strength (RSSI)
2. Increase heartbeat interval
3. Reduce number of devices on network
4. Use wired Ethernet instead of WiFi

### Issue: ESP32 resets randomly

**Symptoms:** Device keeps rebooting

**Solutions:**
1. Use stable 5V power supply
2. Check power consumption (WiFi uses ~240mA)
3. Reduce WiFi TX power
4. Disable WiFi when not needed

---

## Performance Specifications

| Metric | Value | Notes |
|--------|-------|-------|
| Button scan rate | 100 Hz | 10ms per scan |
| Debounce | 50ms | Prevents false triggers |
| HTTP timeout | 5 seconds | WiFi can be slow |
| Heartbeat interval | 60 seconds | Shows device alive |
| WiFi reconnect | 30 seconds | Auto-reconnect on disconnect |
| Max devices | 50+ | Depends on Flask performance |
| Response time | 100-500ms | WiFi dependent |

---

## Security Considerations

### Current Implementation
- Open WiFi (WPA2 password only)
- No encryption on HTTP messages
- No authentication tokens

### Production Recommendations
1. **Use HTTPS** (configure SSL certificates)
2. **Add authentication** (API keys or tokens)
3. **Firewall** ESP32 network from main network
4. **MAC filtering** on router
5. **Static IPs** for all ESP32s

---

## Testing Checklist

### Basic Connectivity
- [ ] ESP32 connects to WiFi
- [ ] ESP32 registers with Flask
- [ ] Heartbeat working
- [ ] Can ping ESP32 from PC

### Button Functionality
- [ ] All 30 buttons work
- [ ] Emergency type cycles correctly
- [ ] Serial output correct
- [ ] LEDs and buzzer work

### Integration
- [ ] Button press → Flask receives
- [ ] Flask → Frontend updates
- [ ] Multiple triggers work
- [ ] Clear emergencies works

### Reliability
- [ ] WiFi reconnect works
- [ ] Long-term stability (hours)
- [ ] No memory leaks
- [ ] Power consumption acceptable

---

## Advanced Features

### 1. Static IP Assignment
```cpp
IPAddress localIP(192, 168, 1, 101);
IPAddress gateway(192, 168, 1, 1);
IPAddress subnet(255, 255, 255, 0);

WiFi.config(localIP, gateway, subnet);
```

### 2. mDNS (Access by Name)
```cpp
#include <ESPmDNS.h>

MDNS.begin("evacuation-esp32");
// Access at: http://evacuation-esp32.local
```

### 3. Over-The-Air (OTA) Updates
```cpp
#include <ArduinoOTA.h>

void setup() {
  ArduinoOTA.begin();
}

void loop() {
  ArduinoOTA.handle();
}
```

### 4. Deep Sleep (Battery Saving)
```cpp
// Sleep for 10 seconds, then wake up
esp_sleep_enable_timer_wakeup(10 * 1000000);
esp_deep_sleep_start();
```

---

## Comparison with Serial (Arduino)

| Aspect | Serial (Arduino) | WiFi (ESP32) |
|--------|------------------|---------------|
| Setup complexity | Medium | Low |
| Cable required | Yes (data) | No (power only) |
| Range | USB limit (~5m) | WiFi range | 
| Multiple devices | Difficult | Easy |
| Real-time updates | Good | Very good |
| Power consumption | Low | Higher |
| Reliability | Very high | High |
| Cost | Lower | Slightly higher |
| Mobile deployment | No | Yes |

---

## Migration from Arduino

### If Upgrading from Arduino

1. **Keep Flask Backend** - No changes needed
2. **Remove serial_reader.py** - Not needed for ESP32
3. **Delete Arduino code** - Replaced by ESP32 firmware
4. **Add ESP32 device** - New hardware
5. **Update frontend** - Already compatible!

### Compatibility

✅ **Fully compatible** with existing:
- Flask backend (all endpoints work)
- Frontend (no changes needed)
- Pathfinding algorithm (same)
- Building layout (same)

---

## Support

For ESP32-specific issues:
1. Check Serial Monitor output (115200 baud)
2. Verify WiFi credentials
3. Check Flask backend logs
4. Test with simple WiFi sketch first
5. Consult ESP32 documentation

---

## Version History

- **v1.0** (Current)
  - Initial ESP32 support
  - 30-button matrix
  - WiFi connectivity
  - Device management
  - Heartbeat monitoring

---

**Status: ESP32 Integration Complete** ✅
