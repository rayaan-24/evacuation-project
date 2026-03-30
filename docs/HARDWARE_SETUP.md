# Smart Evacuation System - Hardware Setup Guide

## Overview

This guide will help you set up the IoT hardware components for the Smart Evacuation System. The system uses an Arduino Uno with a 5x6 button matrix (30 emergency triggers), LCD display, LED indicators, and buzzer alerts.

---

## Component Shopping List

### Required Components

| Component | Quantity | Estimated Cost | Purpose |
|-----------|----------|---------------|---------|
| Arduino Uno R3 | 1 | $6-10 | Main microcontroller |
| Tactile Push Buttons (6mm x 6mm) | 30 | $2-5 | 5x6 emergency matrix |
| LEDs 5mm (Red, Green, Yellow) | 3 | $1-2 | Status indicators |
| Active Buzzer 5V | 1 | $1-2 | Audio alerts |
| Resistors 220Ω | 4 | $0.50 | LED current limiting |
| 16x2 LCD Display (I2C) | 1 | $4-6 | Status text display |
| I2C LCD Adapter (PCF8574) | 1 | $2-3 | LCD communication |
| USB Cable Type A to B | 1 | $2-3 | Serial connection |
| Jumper Wires | ~40 | $2-3 | Wiring connections |
| Breadboard/Perfboard | 1 | $3-5 | Prototype board |

**Total Estimated Cost: $24-39 USD**

---

## Pin Configuration

### Button Matrix (5x6 = 30 buttons)

```
Row Pins (OUTPUT):  2, 3, 4, 5, 6
Col Pins (INPUT):   7, 8, 9, 10, 11, 12
```

### Status Indicators

```
LED Green:   A1 (Analog pin 1)
LED Yellow:  A2 (Analog pin 2)
LED Red:     A3 (Analog pin 3)
Buzzer:      A0 (Analog pin 0)
```

### LCD Display (I2C)

```
LCD SDA:  A4 (SDA pin on Uno)
LCD SCL:  A5 (SCL pin on Uno)
```

---

## Wiring Diagram

### Button Matrix Wiring

```
Arduino Uno          5x6 Button Matrix
===========         ================
Pin 2 (ROW 0)  -->  Row 0 (5 buttons)
Pin 3 (ROW 1)  -->  Row 1 (5 buttons)
Pin 4 (ROW 2)  -->  Row 2 (5 buttons)
Pin 5 (ROW 3)  -->  Row 3 (5 buttons)
Pin 6 (ROW 4)  -->  Row 4 (5 buttons)

Arduino GND     -->  All button columns (common ground)
Pin 7 (COL 0)  -->  Column 0
Pin 8 (COL 1)  -->  Column 1
Pin 9 (COL 2)  -->  Column 2
Pin 10 (COL 3) -->  Column 3
Pin 11 (COL 4) -->  Column 4
Pin 12 (COL 5) -->  Column 5
```

### LED Status Indicators

```
Arduino Uno         LEDs (with 220Ω resistors)
===========         ========================
Pin A1 (Green)  -->  Green LED (+) --> 220Ω --> GND
Pin A2 (Yellow) -->  Yellow LED(+) --> 220Ω --> GND
Pin A3 (Red)    -->  Red LED (+)   --> 220Ω --> GND
```

### Buzzer Connection

```
Arduino Uno         Buzzer
===========         ======
Pin A0          -->  Buzzer (+)
Arduino GND     -->  Buzzer (-)
```

### LCD Display (I2C)

```
Arduino Uno         I2C LCD Adapter
===========         ===============
A4 (SDA)       -->  SDA pin
A5 (SCL)       -->  SCL pin
5V              -->  VCC
GND             -->  GND
```

---

## Assembly Instructions

### Step 1: Prepare the Arduino

1. Connect Arduino to your computer via USB cable
2. Install Arduino IDE if not already installed
3. Download LiquidCrystal_I2C library

### Step 2: Wire the Button Matrix

1. Connect row pins (2-6) to rows of buttons
2. Connect column pins (7-12) with pull-down configuration
3. Use internal INPUT_PULLUP mode (no external resistors needed)

### Step 3: Connect Status LEDs

1. Insert LEDs into breadboard
2. Connect 220Ω resistors in series with each LED
3. Connect to Arduino analog pins A1, A2, A3

### Step 4: Wire the Buzzer

1. Connect buzzer positive to Arduino A0
2. Connect buzzer negative to GND

### Step 5: Connect LCD Display

1. Solder I2C adapter to LCD display (if not pre-assembled)
2. Connect SDA to A4, SCL to A5
3. Connect VCC to 5V, GND to GND

---

## Software Installation

### 1. Install Arduino IDE

Download from: https://www.arduino.cc/en/software

### 2. Install Required Libraries

In Arduino IDE:
1. Go to **Sketch > Include Library > Manage Libraries**
2. Search and install:
   - `LiquidCrystal_I2C` by Frank de Brabander
   - `Wire.h` (built-in)

### 3. Upload the Firmware

1. Open `iot/enhanced/arduino_enhanced.ino` in Arduino IDE
2. Select **Tools > Board > Arduino Uno**
3. Select correct COM port under **Tools > Port**
4. Click **Upload** (Ctrl+U)

### 4. Verify Installation

1. Open Serial Monitor (9600 baud)
2. You should see: `=== Smart Evacuation System v2.0 ===`
3. Press any button - should see: `SENSOR:sensor_X,TYPE:TYPE`

---

## Testing the Setup

### Basic Functionality Test

1. **Power On**: System displays "Smart Evacuation" on LCD
2. **Button Test**: Press buttons 0-29 - each triggers different sensor
3. **LED Test**: Send `TEST` command via serial
4. **LCD Test**: LCD should show status updates

### Serial Communication Test

```bash
# Check status
SEND: STATUS?

# Run self-test
SEND: TEST

# Clear emergency
SEND: CLEAR
```

---

## Troubleshooting

### LCD Not Displaying

- Check I2C address (default: 0x27)
- Verify SDA/SCL connections
- Check LCD contrast (potentiometer on I2C adapter)

### Buttons Not Responding

- Verify row pins are OUTPUT
- Verify column pins are INPUT_PULLUP
- Check for loose connections

### Serial Not Working

- Check USB cable
- Verify correct COM port selected
- Set Serial Monitor to 9600 baud

### LEDs Not Lighting

- Check polarity (long leg = positive)
- Verify 220Ω resistors are in place
- Test each LED individually

---

## Power Requirements

- **USB Power**: 5V @ 500mA (sufficient for basic setup)
- **External Power**: 7-12V DC @ 1A (for extended use)
- **Current Draw**:
  - Arduino Uno: ~50mA
  - LCD Backlight: ~40mA
  - Buzzer: ~30mA
  - LEDs: ~20mA
  - Total: ~140mA

---

## Next Steps

After hardware setup:
1. Connect Arduino to PC
2. Start Flask backend: `cd backend && python app.py`
3. Run serial reader: `cd backend && python serial_reader.py`
4. Open frontend: http://localhost:5000

---

## Safety Notes

- Always disconnect power before wiring
- Use 220Ω resistors for LEDs to prevent burnout
- Don't exceed 5V on any pin
- Keep wiring organized to prevent shorts
