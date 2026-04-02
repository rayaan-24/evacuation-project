# Wokwi ESP32 Simulation - Step-by-Step Tutorial
# Smart Emergency Evacuation System

---

## What is Wokwi?

Wokwi is an online ESP32/Arduino simulator where you can:
- Build and test circuits virtually
- Upload your actual ESP32 code
- Test WiFi connections (virtual)
- Debug without buying hardware

---

## Step 1: Create Wokwi Account

1. Go to **[wokwi.com](https://wokwi.com)**
2. Click **"Sign Up"** (top right)
3. Choose **"Sign up with GitHub"** (easiest)
4. Authorize the app

---

## Step 2: Create New Project

1. Click **"New Project"** button
2. Select **"ESP32"** from the board list
3. You'll see an empty workspace with ESP32 DevKit

---

## Step 3: Understand the Wokwi Interface

```
┌─────────────────────────────────────────────────────────────────┐
│  Wokwi Workspace                                                │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────┐    ┌──────────────────────────────────────┐  │
│  │ PARTS PANEL  │    │                                       │  │
│  │              │    │                                       │  │
│  │ [Search box] │    │         CIRCUIT CANVAS                │  │
│  │              │    │                                       │  │
│  │ - Resistor   │    │         (Drag components here)        │  │
│  │ - LED        │    │                                       │  │
│  │ - Button     │    │                                       │  │
│  │ - Breadboard │    │                                       │  │
│  │ - etc.       │    │                                       │  │
│  │              │    │                                       │  │
│  └──────────────┘    └──────────────────────────────────────┘  │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │ FILES PANEL                                               │   │
│  │                                                            │   │
│  │ 📄 diagram.json   (Circuit configuration)                │   │
│  │ 📄 sketch.ino     (Your ESP32 code)                       │   │
│  │ 📄 library.json   (Dependencies)                          │   │
│  │                                                            │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Step 4: Add Components

### 4.1 Add Breadboard
1. In Parts Panel, search **"breadboard"**
2. Drag **"Breadboard 400"** to canvas
3. Place it below the ESP32

### 4.2 Add Buttons (5 at a time for demo)
For the full project, you need 30 buttons. For testing, start with 5:

1. Search **"button"** in Parts Panel
2. Drag 5 buttons to the breadboard
3. Arrange them in a row

### 4.3 Add Resistors
1. Search **"resistor"**
2. Drag 3 resistors to breadboard
3. Set value: **220** (click on resistor, change value)

### 4.4 Add LEDs
1. Search **"LED"**
2. Drag 3 LEDs (Red, Yellow, Green) to breadboard

---

## Step 5: Wire Components

### 5.1 Wire Buttons (Matrix 5x6)

**Row Connections (GPIO 4-8):**

1. Click on **ESP32 GPIO4** pin
2. Click on **Button 0 leg 1**
3. A wire connects them

**Column Connections (GPIO 9-14):**

1. Click on **ESP32 GPIO9** pin
2. Click on **Button 0 leg 2**

**Ground (GND):**

1. Click on **ESP32 GND** pin
2. Click on **all other button legs** (leg 3)

### 5.2 Wire LEDs

**Red LED:**
1. Click **ESP32 GPIO15**
2. Click **Resistor leg 1**
3. Click **Resistor leg 2**
4. Click **Red LED Anode (+, long leg)**
5. Click **ESP32 GND**

**Repeat for Yellow (GPIO16) and Green (GPIO17)**

---

## Step 6: Configure Code Files

### 6.1 Open sketch.ino
Click on **sketch.ino** in the Files Panel

### 6.2 Copy Your Code
Delete the default code and paste your ESP32 code from:
`esp32/firmware/esp32_emergency_controller/esp32_emergency_controller.ino`

### 6.3 Modify for Simulation
Add at the top of your code (optional for simulation):
```cpp
// Uncomment for Wokwi simulation
// #define WOKWI_SIMULATION
```

---

## Step 7: Add Virtual WiFi (Optional)

1. Click **"Virtual Devices"** button (bottom right)
2. Click **"Add WiFi Station"**
3. Configure:
   - SSID: `Wokwi_Guest`
   - Password: `12345678`

This simulates WiFi connection.

---

## Step 8: Configure API URL

Since this is simulation, you'll need a real API. Deploy to Render first (see Phase 1).

Update your `config.h`:
```cpp
#define API_HOST "https://https://evacuation-project.onrender.com/"
```

For testing without real API, use the IoT Control Panel directly.

---

## Step 9: Run Simulation

### 9.1 Start
Click the **Play** button (▶️) at the top

### 9.2 Monitor Output
Click **"Serial Monitor"** to see debug output

### 9.3 Test Buttons
Click on buttons in the circuit to simulate presses

### 9.4 Watch Serial Monitor
You should see:
```
Button 0 pressed
Sending to API...
WiFi connected
POST /sensor-update: 200 OK
```

---

## Step 10: Debug Common Issues

### Issue: Buttons not responding
- Check wiring connections
- Ensure buttons are properly placed on breadboard

### Issue: Serial monitor shows nothing
- Click Serial Monitor button
- Check baud rate is 115200
- Press ESP32 reset button (in simulation)

### Issue: WiFi not connecting
- Use virtual WiFi station
- Or: Deploy backend and configure correct API URL

---

## Simplified Test Circuit (5 Buttons)

If 30 buttons is too complex for testing, start with 5:

```
┌─────────────────────────────────────────────────┐
│  ESP32 DevKit                                   │
│  ┌───────────────────────────────────────────┐  │
│  │ GPIO4 ──────────────────────────┐         │  │
│  │ GPIO9 ─────────────────────┐     │         │  │
│  │ GND   ────────────────────┼─────┼───────┐ │  │
│  └───────────────────────────────────────────┘  │
│                                                 │
│  Breadboard                                     │
│  ┌────────────────────────────────────────────┐ │
│  │                                              │ │
│  │  [Btn0] [Btn1] [Btn2] [Btn3] [Btn4]        │ │
│  │    │       │       │       │       │       │ │
│  │    └───────┴───────┴───────┴───────┴───────┘ │
│  │           (All leg 1 connected)              │ │
│  │                                              │ │
│  └────────────────────────────────────────────┘ │
│                                                 │
│  [220Ω]──[RED LED]── GND                       │
│  GPIO15                                         │
│                                                 │
└─────────────────────────────────────────────────┘
```

---

## Importing the Pre-made Diagram

Instead of building from scratch, you can import the `wokwi_diagram.json`:

1. Go to **[wokwi.com/editor](https://wokwi.com/editor)**
2. Click **"Import"** or **"Open"**
3. Paste contents of `docs/wiring_diagrams/wokwi_diagram.json`
4. The circuit loads automatically

---

## Testing Your Full Code

After setting up the circuit:

1. Open `sketch.ino`
2. Replace code with your ESP32 firmware code
3. Run simulation
4. Press buttons
5. Check Serial Monitor for output

---

## Video Tutorial Links

- Wokwi ESP32 Tutorial: https://docs.wokwi.com/get-started/esp32
- Arduino Simulator: https://wokwi.com/arduino

---

## Summary: Wokwi Workflow

```
1. Sign up at wokwi.com
        ↓
2. Create new ESP32 project
        ↓
3. Add breadboard + components
        ↓
4. Wire according to guide
        ↓
5. Paste ESP32 code in sketch.ino
        ↓
6. Configure API URL (after Render deploy)
        ↓
7. Run simulation
        ↓
8. Test button presses
        ↓
9. Verify Serial Monitor output
        ↓
10. Deploy to real hardware when ready
```

---

## Next Steps

1. **First:** Deploy backend to Render (Phase 1)
2. **Then:** Test with Wokwi simulation
3. **Finally:** Build real hardware circuit

---

## Need Help?

- Wokwi Docs: https://docs.wokwi.com
- Wokwi Discord: https://wokwi.com/discord
- Project Issues: Create issue on GitHub
