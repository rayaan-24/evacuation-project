# Testing Checklist - Smart Evacuation System

## Pre-Testing Checklist

### Hardware Assembly
- [ ] All 30 buttons wired correctly
- [ ] LEDs connected with 220Ω resistors
- [ ] Buzzer connected
- [ ] LCD display connected (I2C)
- [ ] USB cable connected
- [ ] No loose connections
- [ ] No short circuits

### Software Installation
- [ ] Arduino IDE installed
- [ ] LiquidCrystal_I2C library installed
- [ ] Firmware uploaded successfully
- [ ] Python dependencies installed: `pip install flask flask-cors pyserial requests`

---

## Testing Phases

## Phase 1: Arduino Hardware Tests

### Test 1.1: Power On
```
Expected: LCD displays "Smart Evacuation" then "SYSTEM READY"
Status:  [ ]
```

### Test 1.2: Serial Communication
```
Action:   Open Serial Monitor at 9600 baud
Expected: See initialization messages
         "=== Smart Evacuation System v2.0 ==="
         "READY - 30-sensor emergency console active"
Status:  [ ]
```

### Test 1.3: Button Matrix (All 30 buttons)
```
Action:   Press each button (0-29) one at a time
Expected: Serial output: "SENSOR:sensor_X,TYPE:FIRE"
         (Note: Type cycles through FIRE->SMOKE->GAS->BLOCKAGE->CROWD)
Status:  [ ]
```

### Test 1.4: LED Indicators
```
Action:   Send "TEST" command via serial
Expected: 
  - Green LED blinks
  - Yellow LED blinks
  - Red LED blinks
  - Buzzer sounds
Status:  [ ]
```

### Test 1.5: LCD Status Updates
```
Action:   Press a button
Expected: LCD shows:
  Line 1: "! EMERGENCY !"
  Line 2: "TYPE S##:CORRIDOR"
Status:  [ ]
```

### Test 1.6: Status Query
```
Action:   Send "STATUS?" via serial
Expected: Response with system status
Status:  [ ]
```

### Test 1.7: Emergency Clear
```
Action:   Send "CLEAR" via serial
Expected: Emergency cleared, LCD shows "SYSTEM READY"
Status:  [ ]
```

### Test 1.8: System Reset
```
Action:   Send "RESET" via serial
Expected: System resets, counters cleared
Status:  [ ]
```

---

## Phase 2: Backend Tests

### Test 2.1: Flask Server Startup
```
Command:  cd backend && python app.py
Expected: "Smart Evacuation backend listening at http://localhost:5000"
Status:  [ ]
```

### Test 2.2: API Home Endpoint
```
URL:      http://localhost:5000/api
Expected: JSON response with API info
Status:  [ ]
```

### Test 2.3: Layout Endpoint
```
URL:      http://localhost:5000/layout
Expected: JSON with building layout data
Status:  [ ]
```

### Test 2.4: Find Path (Basic)
```
Command:  curl -X POST http://localhost:5000/find-path \
  -H "Content-Type: application/json" \
  -d '{"start_room": "G07"}'
Expected: JSON with path and directions
Status:  [ ]
```

### Test 2.5: Find Path (With Emergency)
```
Command:  curl -X POST http://localhost:5000/find-path \
  -H "Content-Type: application/json" \
  -d '{"start_room": "G07", "emergencies": [{"location": "C1A", "type": "FIRE"}]}'
Expected: JSON with safe path avoiding C1A
Status:  [ ]
```

### Test 2.6: Sensor Update
```
Command:  curl -X POST http://localhost:5000/sensor-update \
  -H "Content-Type: application/json" \
  -d '{"sensor_id": "sensor_0", "type": "FIRE"}'
Expected: {"status": "updated", ...}
Status:  [ ]
```

### Test 2.7: Sensor Status
```
URL:      http://localhost:5000/sensor-status
Expected: JSON with active emergencies
Status:  [ ]
```

### Test 2.8: Reset Emergencies
```
Command:  curl -X POST http://localhost:5000/reset-emergencies
Expected: All emergencies cleared
Status:  [ ]
```

---

## Phase 3: Serial Reader Tests

### Test 3.1: Demo Mode (No Arduino)
```
Command:  python serial_reader.py demo
Expected: Simulated sensor events sent to backend
Status:  [ ]
```

### Test 3.2: Live Serial Connection
```
Command:  python serial_reader.py --port COM3
         (Replace COM3 with your port)
Expected: Connected to Arduino, forwarding events
Status:  [ ]
```

---

## Phase 4: Frontend Tests

### Test 4.1: Frontend Load
```
URL:      http://localhost:5000/
Expected: Page loads with building map
Status:  [ ]
```

### Test 4.2: Room Selection
```
Action:   Select a room from dropdown
Expected: Room is selected
Status:  [ ]
```

### Test 4.3: Corridor Selection
```
Action:   Check a corridor checkbox
Expected: Corridor marked as emergency zone
Status:  [ ]
```

### Test 4.4: Run Evacuation
```
Action:   Select room, select corridor, click "RUN EVACUATION"
Expected: 
  - Path animates on map
  - Directions appear
  - Stats update
Status:  [ ]
```

### Test 4.5: Reset Map
```
Action:   Click "Reset Map"
Expected: All selections cleared, map reset
Status:  [ ]
```

### Test 4.6: Multiple Emergencies
```
Action:   Select multiple corridors with different types
Expected: All hazards displayed with correct colors
Status:  [ ]
```

### Test 4.7: Mobile Responsive
```
Action:   Open on mobile device or resize browser
Expected: Layout adjusts for screen size
Status:  [ ]
```

### Test 4.8: Sound Toggle
```
Action:   Click sound toggle button
Expected: Sound enabled/disabled
Status:  [ ]
```

---

## Phase 5: Integration Tests

### Test 5.1: Arduino → Backend → Frontend
```
Action:   Press button on Arduino
Expected: 
  1. Arduino sends serial data
  2. Serial reader forwards to backend
  3. Frontend receives update
  4. Map updates in real-time
Status:  [ ]
```

### Test 5.2: Dynamic Re-routing
```
Action:   
  1. Run evacuation
  2. While animating, trigger new emergency on route
Expected: Path recalculates avoiding new hazard
Status:  [ ]
```

### Test 5.3: All Exits Blocked
```
Action:   Trigger emergencies at ALL corridor junctions
Expected: Error message "No safe path found"
Status:  [ ]
```

### Test 5.4: Auto-Clear Emergency
```
Action:   Trigger emergency, wait 60 seconds
Expected: Emergency auto-clears
Status:  [ ]
```

---

## Phase 6: Performance Tests

### Test 6.1: ACO Response Time
```
Action:   Measure time from "Run" click to path display
Expected: < 5 seconds
Status:  [ ]
```

### Test 6.2: Serial Latency
```
Action:   Press button, measure time to frontend update
Expected: < 500ms
Status:  [ ]
```

### Test 6.3: Multiple Simultaneous Requests
```
Action:   Rapidly click "Run Evacuation" multiple times
Expected: Only latest request processed
Status:  [ ]
```

---

## Test Results Summary

| Test Phase | Passed | Failed | Total |
|------------|--------|--------|-------|
| Phase 1: Hardware | 0 | 0 | 8 |
| Phase 2: Backend | 0 | 0 | 8 |
| Phase 3: Serial Reader | 0 | 0 | 2 |
| Phase 4: Frontend | 0 | 0 | 8 |
| Phase 5: Integration | 0 | 0 | 4 |
| Phase 6: Performance | 0 | 0 | 3 |
| **TOTAL** | **0** | **0** | **33** |

---

## Known Issues

| Issue # | Description | Severity | Status |
|---------|-------------|----------|--------|
| 1 | | | |
| 2 | | | |
| 3 | | | |

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
Additional notes and observations:














```
