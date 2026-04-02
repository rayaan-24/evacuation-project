# ESP32 Emergency Controller - Complete Wiring Guide
# Smart Emergency Evacuation System

---

## Overview

This document provides complete wiring instructions for the ESP32 Emergency Controller with a 30-button matrix (5x6) for emergency corridor selection.

---

## Components Required

| Component | Quantity | Purpose |
|-----------|----------|---------|
| ESP32 DevKit v1 | 1 | Main microcontroller |
| Breadboard (half-size) | 1 | Prototyping board |
| Tactile Push Buttons | 30 | Emergency input matrix |
| Red LED | 1 | Error/Warning indicator |
| Yellow LED | 1 | Processing indicator |
| Green LED | 1 | Success indicator |
| Resistor 220Ω | 3 | LED current limiting |
| Jumper Wires | ~50 | Connections |

---

## GPIO Pin Assignment

```
┌────────────────────────────────────────────────────────────┐
│                    ESP32 DevKit v1                          │
├────────────────────────────────────────────────────────────┤
│                                                              │
│  POWER:                                                       │
│    3.3V  ──────── Not used for buttons (use internal pullup) │
│    5V    ──────── Not connected                              │
│    GND   ──────── LED cathodes, button common               │
│                                                              │
│  ROW PINS (OUTPUT - Drive LOW to scan row):                  │
│    GPIO 4  ──── Row 0 (Buttons 0-5)                         │
│    GPIO 5  ──── Row 1 (Buttons 6-11)                        │
│    GPIO 6  ──── Row 2 (Buttons 12-17)                       │
│    GPIO 7  ──── Row 3 (Buttons 18-23)                       │
│    GPIO 8  ──── Row 4 (Buttons 24-29)                       │
│                                                              │
│  COLUMN PINS (INPUT_PULLUP - Read button state):             │
│    GPIO 9  ──── Column 0                                    │
│    GPIO 10 ──── Column 1                                    │
│    GPIO 11 ──── Column 2                                    │
│    GPIO 12 ──── Column 3                                    │
│    GPIO 13 ──── Column 4                                    │
│    GPIO 14 ──── Column 5                                    │
│                                                              │
│  STATUS LEDS (OUTPUT):                                       │
│    GPIO 15 ──── Red LED (via 220Ω resistor)                 │
│    GPIO 16 ──── Yellow LED (via 220Ω resistor)              │
│    GPIO 17 ──── Green LED (via 220Ω resistor)               │
│                                                              │
└────────────────────────────────────────────────────────────┘
```

---

## Button Matrix Layout

```
            COLUMN 0   COLUMN 1   COLUMN 2   COLUMN 3   COLUMN 4   COLUMN 5
                │          │          │          │          │          │
                │          │          │          │          │          │
    ROW 0  ────┴──────────┴──────────┴──────────┴──────────┴──────────┴─── GPIO 4
    (Btns 0-5)  │          │          │          │          │          │
                │          │          │          │          │          │
    ROW 1  ────┴──────────┴──────────┴──────────┴──────────┴──────────┴─── GPIO 5
    (Btns 6-11) │          │          │          │          │          │
                │          │          │          │          │          │
    ROW 2  ────┴──────────┴──────────┴──────────┴──────────┴──────────┴─── GPIO 6
   (Btns 12-17) │          │          │          │          │          │
                │          │          │          │          │          │
    ROW 3  ────┴──────────┴──────────┴──────────┴──────────┴──────────┴─── GPIO 7
   (Btns 18-23) │          │          │          │          │          │
                │          │          │          │          │          │
    ROW 4  ────┴──────────┴──────────┴──────────┴──────────┴──────────┴─── GPIO 8
   (Btns 24-29) │          │          │          │          │          │
                │          │          │          │          │          │
               GND        GND        GND        GND        GND        GND
                │          │          │          │          │          │
               All columns connect to GND via buttons when pressed
```

---

## Button Number Mapping

Each button has a number (0-29). Here's the mapping:

```
Button Number = Row × 6 + Column

┌─────┬─────┬─────┬─────┬─────┬─────┐
│  0  │  1  │  2  │  3  │  4  │  5  │  ← Row 0
├─────┼─────┼─────┼─────┼─────┼─────┤
│  6  │  7  │  8  │  9  │ 10  │ 11  │  ← Row 1
├─────┼─────┼─────┼─────┼─────┼─────┤
│ 12  │ 13  │ 14  │ 15  │ 16  │ 17  │  ← Row 2
├─────┼─────┼─────┼─────┼─────┼─────┤
│ 18  │ 19  │ 20  │ 21  │ 22  │ 23  │  ← Row 3
├─────┼─────┼─────┼─────┼─────┼─────┤
│ 24  │ 25  │ 26  │ 27  │ 28  │ 29  │  ← Row 4
└─────┴─────┴─────┴─────┴─────┴─────┘
  Col0  Col1  Col2  Col3  Col4  Col5
```

---

## Step-by-Step Wiring Instructions

### Step 1: Prepare Your Components

1. Place ESP32 DevKit on breadboard (across the center groove)
2. Identify GPIO pins on ESP32
3. Organize 30 buttons in a 5×6 grid pattern
4. Get 3 LEDs and 3 resistors ready

### Step 2: Wire the Button Matrix

#### Row Connections (GPIO 4-8)

For each row, connect ONE wire from the GPIO pin to ALL buttons in that row:

```
GPIO 4 ───┬─── (connect to leg 1 of buttons 0, 1, 2, 3, 4, 5)
          ├─── (leg 1 of Button 0)
          ├─── (leg 1 of Button 1)
          ├─── (leg 1 of Button 2)
          ├─── (leg 1 of Button 3)
          ├─── (leg 1 of Button 4)
          └─── (leg 1 of Button 5)

GPIO 5 ───┬─── (connect to leg 1 of buttons 6, 7, 8, 9, 10, 11)
          ├─── (leg 1 of Button 6)
          ... and so on

GPIO 6 ───┬─── (connect to leg 1 of buttons 12, 13, 14, 15, 16, 17)

GPIO 7 ───┬─── (connect to leg 1 of buttons 18, 19, 20, 21, 22, 23)

GPIO 8 ───┬─── (connect to leg 1 of buttons 24, 25, 26, 27, 28, 29)
```

#### Column Connections (GPIO 9-14)

For each column, connect ONE wire from the GPIO pin to ALL buttons in that column:

```
GPIO 9 ───┬─── (connect to leg 2 of buttons 0, 6, 12, 18, 24)
          ├─── (leg 2 of Button 0)
          ├─── (leg 2 of Button 6)
          ├─── (leg 2 of Button 12)
          ├─── (leg 2 of Button 18)
          └─── (leg 2 of Button 24)

GPIO 10 ──┬─── (connect to leg 2 of buttons 1, 7, 13, 19, 25)

GPIO 11 ──┬─── (connect to leg 2 of buttons 2, 8, 14, 20, 26)

GPIO 12 ──┬─── (connect to leg 2 of buttons 3, 9, 15, 21, 27)

GPIO 13 ──┬─── (connect to leg 2 of buttons 4, 10, 16, 22, 28)

GPIO 14 ──┬─── (connect to leg 2 of buttons 5, 11, 17, 23, 29)
```

#### Common Ground Connection

Connect ALL remaining button legs (not already connected to columns) to ESP32 GND:

```
ESP32 GND ──┬─── (connect to leg 3 of all 30 buttons)
            ├─── (leg 3 of Button 0)
            ├─── (leg 3 of Button 1)
            ├─── (leg 3 of Button 2)
            ... (all 30 buttons)
```

### Step 3: Wire the Status LEDs

#### Red LED (GPIO 15)
```
GPIO 15 ──── 220Ω Resistor ──── Red LED (+) ──── GND
              (Leg 1)           (Long leg/Anode)
```

#### Yellow LED (GPIO 16)
```
GPIO 16 ──── 220Ω Resistor ──── Yellow LED (+) ──── GND
              (Leg 1)            (Long leg/Anode)
```

#### Green LED (GPIO 17)
```
GPIO 17 ──── 220Ω Resistor ──── Green LED (+) ──── GND
              (Leg 1)            (Long leg/Anode)
```

---

## Visual Breadboard Layout

```
╔══════════════════════════════════════════════════════════════════════════╗
║                        BREADBOARD VIEW                                   ║
║                                                                          ║
║    ESP32 DevKit                                                          ║
║    ┌─────────────────────────────────────────────────────────┐          ║
║    │  3.3V  5V  GND  GPIO 4  5  6  7  8  9  10  11  12  13  │          ║
║    │                                                          │          ║
║    │  3.3V  5V  GND  15  16  17  EN  TX  RX  D2  D4  SD2  SD3│          ║
║    └─────────────────────────────────────────────────────────┘          ║
║         │                                                           │    ║
║         │  + (positive rail)                                        │    ║
║    ═════╧═══════════════════════════════════════════════════════════    ║
║         │                                                           │    ║
║    ┌────┴─────────────────────────────────────────────────────┐    │    ║
║    │                                                        │    │    ║
║    │    [Btn 0] [Btn 1] [Btn 2] [Btn 3] [Btn 4] [Btn 5]   │    │    ║
║    │       │       │       │       │       │                │    │    ║
║    │       └───────┴───────┴───────┴───────┴───────┐        │    │    ║
║    │           All Leg 1s connected together       │        │    │    ║
║    │                                             │        │    │    ║
║    │    [Btn 6] [Btn 7] [Btn 8] [Btn 9] [Btn10] [Btn11]  │    │    ║
║    │       │       │       │       │        │                │    │    ║
║    │       └───────┴───────┴───────┴────────┴───────┐       │    │    ║
║    │                                             │       │    │    ║
║    │    [Btn12] [Btn13] [Btn14] [Btn15] [Btn16] [Btn17]  │    │    ║
║    │       │       │       │       │        │               │    │    ║
║    │       └───────┴───────┴───────┴────────┴───────┐      │    │    ║
║    │                                             │      │    │    ║
║    │    [Btn18] [Btn19] [Btn20] [Btn21] [Btn22] [Btn23]  │    │    ║
║    │       │       │       │       │        │               │    │    ║
║    │       └───────┴───────┴───────┴────────┴───────┐     │    │    ║
║    │                                             │     │    │    ║
║    │    [Btn24] [Btn25] [Btn26] [Btn27] [Btn28] [Btn29]  │    │    ║
║    │       │       │       │       │        │               │    │    ║
║    │       └───────┴───────┴───────┴────────┴───────┘      │    │    ║
║    │                                                        │    │    ║
║    └────────────────────────────────────────────────────────┘    │    ║
║         │                                                           │    ║
║    ═════╧═══════════════════════════════════════════════════════════    ║
║         │  - (negative rail / GND)                                 │    ║
║         │                                                           │    ║
║         └── GPIO 15 ──[220Ω]──[RED LED]──┬                         │    ║
║         └── GPIO 16 ──[220Ω]──[YEL LED]──┤── GND                  │    ║
║         └── GPIO 17 ──[220Ω]──[GRN LED]──┘                         │    ║
║                                                                          ║
╚══════════════════════════════════════════════════════════════════════════╝
```

---

## Pin Configuration Summary

| GPIO | Direction | Purpose | Color in Diagram |
|------|-----------|---------|-----------------|
| GPIO 4 | OUTPUT | Row 0 scan | Orange |
| GPIO 5 | OUTPUT | Row 1 scan | Orange |
| GPIO 6 | OUTPUT | Row 2 scan | Orange |
| GPIO 7 | OUTPUT | Row 3 scan | Orange |
| GPIO 8 | OUTPUT | Row 4 scan | Orange |
| GPIO 9 | INPUT_PULLUP | Column 0 read | Blue |
| GPIO 10 | INPUT_PULLUP | Column 1 read | Blue |
| GPIO 11 | INPUT_PULLUP | Column 2 read | Blue |
| GPIO 12 | INPUT_PULLUP | Column 3 read | Blue |
| GPIO 13 | INPUT_PULLUP | Column 4 read | Blue |
| GPIO 14 | INPUT_PULLUP | Column 5 read | Blue |
| GPIO 15 | OUTPUT | Red LED | Red |
| GPIO 16 | OUTPUT | Yellow LED | Yellow |
| GPIO 17 | OUTPUT | Green LED | Green |
| GND | POWER | Common ground | Black |

---

## Testing Checklist

### Before powering on, verify:

- [ ] All 30 buttons are properly placed
- [ ] Row connections (GPIO 4-8) are not shorted together
- [ ] Column connections (GPIO 9-14) are not shorted together
- [ ] All buttons connect to GND when pressed
- [ ] LEDs are connected with 220Ω resistors
- [ ] LED polarity is correct (long leg to resistor, short leg to GND)

### Power on tests:

- [ ] ESP32 powers on (blue LED on board)
- [ ] Serial monitor shows "WiFi connecting..."
- [ ] All 30 buttons register when pressed
- [ ] LEDs light up as expected

---

## Troubleshooting

### Problem: Button not responding
1. Check row connection wire
2. Check column connection wire
3. Verify button is properly seated
4. Check for cold solder joints (if soldered)

### Problem: Multiple buttons triggering
1. Check for short between row wires
2. Check for short between column wires
3. Verify button orientation

### Problem: LED not lighting
1. Check LED polarity (long leg = +)
2. Verify 220Ω resistor is in series
3. Test LED with multimeter

### Problem: ESP32 not powering
1. Check USB cable (use data cable, not charge-only)
2. Verify USB connection
3. Try different USB port

---

## Safety Notes

1. **Always disconnect power before wiring**
2. **Never connect 5V to ESP32 GPIO pins** (they're 3.3V max)
3. **Use resistors with LEDs** to prevent damage
4. **Double-check polarity** of LEDs and capacitors
5. **Don't exceed 3.3V on GPIO pins**

---

## Next Steps

After wiring is complete:
1. Configure WiFi credentials in `config.h`
2. Set API endpoint URL in `config.h`
3. Upload firmware using Arduino IDE
4. Test the system

See `ESP32_INTEGRATION.md` for configuration instructions.
