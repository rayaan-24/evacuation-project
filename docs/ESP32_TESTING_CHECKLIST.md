# ESP32 System Testing Checklist

## Pre-Testing Checklist

### Hardware ✅
- [ ] ESP32 DevKit v1 acquired
- [ ] Breadboard (830 points)
- [ ] 30 tactile buttons (6×6mm)
- [ ] Jumper wires (40+)
- [ ] 3 LEDs (Red, Yellow, Green)
- [ ] 3 resistors (220Ω)
- [ ] Active buzzer (5V)
- [ ] USB cable (data capable)
- [ ] 5V/2A power adapter (optional)

### Software ✅
- [ ] Arduino IDE installed (v1.8+)
- [ ] ESP32 board support added
- [ ] ArduinoJson library installed
- [ ] Python 3.7+ installed
- [ ] Flask and dependencies installed

### Configuration ✅
- [ ] WiFi credentials configured in config.h
- [ ] API_HOST set to your PC's IP
- [ ] DEVICE_ID set (unique per ESP32)
- [ ] DEVICE_LOCATION set

---

## Phase 1: Basic Hardware Test

### Test 1.1: ESP32 Power On
```
Action:   Connect ESP32 via USB
Expected: Blue LED on, Serial Monitor output
Status:   [ ]
```

### Test 1.2: Upload Firmware
```
Action:   Upload esp32_emergency_controller.ino
Expected: "Done uploading" message
Status:   [ ]
```

### Test 1.3: Serial Monitor Output
```
Action:   Open Serial Monitor at 115200 baud
Expected: Header printed, WiFi connection messages
Status:   [ ]
```

---

## Phase 2: WiFi Connection Test

### Test 2.1: WiFi Connection
```
Action:   Wait for ESP32 to connect
Expected: "✓ WiFi Connected!" in Serial Monitor
          IP Address shown (e.g., 192.168.1.101)
Status:   [ ]
```

### Test 2.2: Registration
```
Action:   ESP32 auto-registers on boot
Expected: "✓ Device registered successfully!" in Serial Monitor
Status:   [ ]
```

### Test 2.3: Backend Device List
```
Action:   curl http://localhost:5000/esp32/devices
Expected: JSON with registered device
Status:   [ ]
```

---

## Phase 3: Button Matrix Test

### Test 3.1: Single Button Press
```
Action:   Press button 0 (top-left)
Expected: Serial output:
          🔴 EMERGENCY TRIGGERED!
          Button: 0 (C1A-North)
          Sensor: sensor_0
          Type:   FIRE
Status:   [ ]
```

### Test 3.2: Emergency Type Cycling
```
Action:   Press button 0 again (without pressing other buttons)
Expected: Type changes: FIRE → SMOKE → GAS → BLOCKAGE → CROWD → FIRE
Status:   [ ]
```

### Test 3.3: All 30 Buttons
```
Action:   Press buttons 0-29 one by one
Expected: All buttons respond, sensor IDs increment correctly
Status:   [ ]
```

### Test 3.4: Button Labels
```
Action:   Press various buttons, check Serial output
Expected: Labels match button positions (C1A, C2A, etc.)
Status:   [ ]
```

---

## Phase 4: Status Indicators Test

### Test 4.1: LED Indicators
```
Action:   Press any button
Expected: Red LED flashes 3 times rapidly
Status:   [ ]
```

### Test 4.2: Buzzer
```
Action:   Press any button
Expected: Buzzer beeps 3 times with LED
Status:   [ ]
```

### Test 4.3: WiFi LED
```
Action:   Monitor built-in LED
Expected: Solid blue when connected, off when disconnected
Status:   [ ]
```

### Test 4.4: Green LED (Ready State)
```
Action:   After successful WiFi connection
Expected: Green LED stays on (system ready)
Status:   [ ]
```

---

## Phase 5: Backend Integration Test

### Test 5.1: Flask Backend Startup
```
Action:   cd backend && python app.py
Expected: "Listening at http://localhost:5000"
          "ESP32 WiFi mode: enabled"
Status:   [ ]
```

### Test 5.2: API Endpoint
```
Action:   curl http://localhost:5000/api
Expected: JSON response with API info
Status:   [ ]
```

### Test 5.3: ESP32 Registration Endpoint
```
Action:   curl http://localhost:5000/esp32/devices
Expected: JSON with registered ESP32 device
Status:   [ ]
```

### Test 5.4: Sensor Update Endpoint
```
Action:   Press button on ESP32
Expected: Backend receives POST to /sensor-update
          Log shows: "Sensor update sensor=sensor_X..."
Status:   [ ]
```

### Test 5.5: Heartbeat
```
Action:   Wait 60 seconds (automatic)
Expected: Serial Monitor shows heartbeat sent
          Backend receives /esp32/heartbeat
Status:   [ ]
```

---

## Phase 6: Frontend Integration Test

### Test 6.1: Frontend Load
```
Action:   Open browser to http://localhost:5000/
Expected: Building map renders correctly
          IoT Sensor Status panel visible
Status:   [ ]
```

### Test 6.2: Emergency Appears
```
Action:   Press button on ESP32
Expected: IoT Sensor Status panel updates
          Sensor shows FIRE (red) or current type
Status:   [ ]
```

### Test 6.3: Multiple Emergencies
```
Action:   Press 3 different buttons
Expected: All 3 sensors show as active
          Dashboard shows "3 Active"
Status:   [ ]
```

### Test 6.4: Real-time Updates
```
Action:   Press button, watch frontend immediately
Expected: Updates appear within 1-2 seconds
Status:   [ ]
```

---

## Phase 7: Pathfinding Test

### Test 7.1: Basic Evacuation (No Blocks)
```
Action:   
  1. Don't press any buttons on ESP32
  2. Select G07 (Smart Classroom) on frontend
  3. Click "RUN EVACUATION"
Expected: 
  - Path displays on map
  - Directions show
  - Stats update (distance, steps, exit)
Status:   [ ]
```

### Test 7.2: Single Block
```
Action:   
  1. Press button 0 on ESP32 (blocks C1A)
  2. Select G07 on frontend
  3. Click "RUN EVACUATION"
Expected: 
  - Path avoids C1A
  - Different exit chosen if C1A was only route
Status:   [ ]
```

### Test 7.3: Multiple Blocks
```
Action:   
  1. Press buttons 0, 4, 8 on ESP32 (blocks 3 corridors)
  2. Select G07 on frontend
  3. Run evacuation
Expected: 
  - Path avoids all 3 blocked corridors
  - Alternative route shown
Status:   [ ]
```

### Test 7.4: Block All Routes
```
Action:   
  1. Press multiple buttons to block all corridors leading to exits
  2. Try to run evacuation
Expected: 
  - "No safe path found" message
  - Modal with instructions
Status:   [ ]
```

---

## Phase 8: Clear Emergencies

### Test 8.1: Clear Single Emergency
```
Action:   Press same button enough times to cycle back to FIRE
          Then clear via frontend or API
Expected: Sensor returns to normal
Status:   [ ]
```

### Test 8.2: Clear All via API
```
Action:   curl -X POST http://localhost:5000/reset-emergencies
Expected: All ESP32-triggered emergencies cleared
          Frontend updates to show no active emergencies
Status:   [ ]
```

### Test 8.3: ESP32 After Clear
```
Action:   After clearing, press new button
Expected: ESP32 sends new emergency normally
          System accepts it
Status:   [ ]
```

---

## Phase 9: WiFi Reliability Test

### Test 9.1: WiFi Disconnect/Reconnect
```
Action:   Turn off WiFi router momentarily
Expected: ESP32 shows "WiFi lost! Reconnecting..."
          Reconnects automatically when WiFi back
Status:   [ ]
```

### Test 9.2: Long-term Stability
```
Action:   Run system for 1 hour
Expected: 
  - No memory leaks
  - Continuous heartbeat
  - Buttons remain responsive
Status:   [ ]
```

### Test 9.3: Multiple Reconnects
```
Action:   WiFi drops 3 times over 30 minutes
Expected: ESP32 reconnects each time
          No data lost
Status:   [ ]
```

---

## Phase 10: Multi-Emergency Scenarios

### Test 10.1: Fire Spreading
```
Action:   Press button 0 → wait 5s → press button 1 → wait 5s → press button 2
Expected: Sequential fires shown
          Path updates to avoid all
Status:   [ ]
```

### Test 10.2: Different Emergency Types
```
Action:   Press button 0 (FIRE) → button 1 (cycles to SMOKE)
Expected: Both corridors show different colors
          Frontend shows FIRE and SMOKE
Status:   [ ]
```

### Test 10.3: Rapid Button Presses
```
Action:   Press 10 different buttons rapidly
Expected: All events captured
          No missed triggers
Status:   [ ]
```

---

## Phase 11: Advanced Features

### Test 11.1: Heartbeat Functionality
```
Action:   Monitor /esp32/devices endpoint over time
Expected: "last_seen" updates every 60 seconds
Status:   [ ]
```

### Test 11.2: Device Status Endpoint
```
Action:   curl http://localhost:5000/esp32/status
Expected: Shows online/offline devices
          RSSI values
Status:   [ ]
```

### Test 11.3: Serial Monitor Logging
```
Action:   Check Serial Monitor during operation
Expected: All events logged with timestamps
          Statistics printed periodically
Status:   [ ]
```

---

## Test Results Summary

| Test Phase | Passed | Failed | Total |
|------------|--------|--------|-------|
| Phase 1: Basic Hardware | 0 | 0 | 3 |
| Phase 2: WiFi Connection | 0 | 0 | 3 |
| Phase 3: Button Matrix | 0 | 0 | 4 |
| Phase 4: Status Indicators | 0 | 0 | 4 |
| Phase 5: Backend Integration | 0 | 0 | 5 |
| Phase 6: Frontend Integration | 0 | 0 | 4 |
| Phase 7: Pathfinding | 0 | 0 | 4 |
| Phase 8: Clear Emergencies | 0 | 0 | 3 |
| Phase 9: WiFi Reliability | 0 | 0 | 3 |
| Phase 10: Multi-Emergency | 0 | 0 | 3 |
| Phase 11: Advanced Features | 0 | 0 | 3 |
| **TOTAL** | **0** | **0** | **39** |

---

## Known Issues

| Issue # | Description | Severity | Status |
|---------|-------------|----------|--------|
| 1 | | | |
| 2 | | | |
| 3 | | | |

---

## Performance Metrics

| Metric | Target | Actual | Status |
|--------|--------|--------|--------|
| WiFi connect time | < 10s | | |
| Button response time | < 100ms | | |
| HTTP send time | < 500ms | | |
| Frontend update time | < 2s | | |
| Memory usage (ESP32) | < 200KB | | |
| Uptime before issues | > 1 hour | | |

---

## Sign-Off

| Role | Name | Date | Signature |
|------|------|------|-----------|
| Developer | | | |
| Tester | | | |
| Reviewer | | | |

---

## Notes

```
Additional observations:



```
