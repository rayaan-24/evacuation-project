# ESP32 + 30-Button IoT System Complete Guide
## Smart Evacuation System - Step-by-Step

**For ESP32 DevKit V1 (DOIT) - Micro-USB on top**

---

# TABLE OF CONTENTS

1. [Your ESP32 Board Explained](#1-your-esp32-board-explained)
2. [Components Required](#2-components-required)
3. [Understanding Your GPIO Pins](#3-understanding-your-gpio-pins)
4. [Why Use a Matrix Design?](#4-why-use-a-matrix-design)
5. [Correct Pin Mapping](#5-correct-pin-mapping)
6. [Physical Wiring Step-by-Step](#6-physical-wiring-step-by-step)
7. [Circuit Explanation](#7-circuit-explanation)
8. [Complete ESP32 Code](#8-complete-esp32-code)
9. [IoT Integration Explained](#9-iot-integration-explained)
10. [Flask Backend Setup](#10-flask-backend-setup)
11. [Testing Procedures](#11-testing-procedures)
12. [Common Mistakes & Solutions](#12-common-mistakes--solutions)
13. [Complete Working Flow](#13-complete-working-flow)

---

# 1. YOUR ESP32 BOARD EXPLAINED

## Your Board: ESP32 DevKit V1 (DOIT)

```
    ╔═══════════════════════════════════════════════════════════════════════╗
    ║                                                                       ║
    ║                     ESP32 DevKit V1 (DOIT)                           ║
    ║                                                                       ║
    ║                          [Micro-USB]                                  ║
    ║                             │││                                      ║
    ║                        ┌────┴┴┴────┐                                 ║
    ║                        │   ESP32    │                                 ║
    ║                        │  WROOM-32  │                                 ║
    ║                        └────────────┘                                 ║
    ║                                                                       ║
    ║   ┌──────────────────────────────────────────────────────────────┐   ║
    ║   │  LEFT SIDE:          │  RIGHT SIDE:                           │   ║
    ║   │  ─────────           │  ──────────                            │   ║
    ║   │  [BOOT] ←            │  → VIN                                 │   ║
    ║   │  3V3                 │  GND                                   │   ║
    ║   │  GND                 │  D13 ←                                 │   ║
    ║   │  D15 ←              │  D12                                   │   ║
    ║   │  D2 ←               │  D14 ←                                 │   ║
    ║   │  D4 ←               │  D27                                   │   ║
    ║   │  RX2                │  D26 ←                                 │   ║
    ║   │  TX2                │  D25 ←                                 │   ║
    ║   │  D5 ←               │  D33                                   │   ║
    ║   │  D18 ←              │  D32                                   │   ║
    ║   │  D19 ←              │  D35 (INPUT ONLY)                      │   ║
    ║   │  D21 ←              │  D34 (INPUT ONLY)                      │   ║
    ║   │  RX0                │  VN   (INPUT ONLY)                     │   ║
    ║   │  TX0                │  VP   (INPUT ONLY)                     │   ║
    ║   │  D22 ←              │  [EN]  ← RESET BUTTON                  │   ║
    ║   │  D23 ←              │                                          │   ║
    ║   └──────────────────────────────────────────────────────────────┘   ║
    ║                                                                       ║
    ╚═══════════════════════════════════════════════════════════════════════╝

    ← = PINS WE WILL USE
```

## Key Features

| Feature | Details |
|---------|---------|
| Operating Voltage | 3.3V (NOT 5V tolerant!) |
| USB Interface | Micro-USB (on top) |
| Boot Button | LEFT side |
| Reset Button | RIGHT side (EN) |
| Built-in LED | D2 (connected to GPIO 2) |
| Wi-Fi | 802.11 b/g/n |
| Bluetooth | Classic + BLE |

---

# 2. COMPONENTS REQUIRED

## Hardware List

| Item | Quantity | Purpose | Est. Cost |
|------|----------|---------|-----------|
| ESP32 DevKit V1 (DOIT) | 1 | Main controller | $8-12 |
| Breadboard (830 points) | 1 | Prototyping | $3-5 |
| Push buttons (6x6mm) | 30 | Emergency triggers | $2-4 |
| Male-to-Male jumper wires | 40 | Wire connections | $2 |
| Male-to-Female jumper wires | 10 | ESP32 to breadboard | $2 |
| Resistors 10kΩ | 6 | Pull-up resistors | $0.50 |
| Resistors 220Ω | 2 | LED current limiting | $0.50 |
| Red LED (5mm) | 1 | Emergency indicator | $0.20 |
| Active buzzer (5V) | 1 | Audio alert | $1 |
| USB cable (Micro-USB) | 1 | Programming + power | $2 |
| **TOTAL** | | | **~$20-30** |

## What Each Component Does

### Breadboard
```
    ┌────────────────────────────────────────────┐
    │ +  +  +  +  +  +  +  +  +  +  +  +  +  + │  ← Positive rail (3.3V)
    │                                            │
    │  ○  ○  ○  ○  ○  ○  ○  ○  ○  ○  ○  ○  ○  ○ │  ← Row holes (buttons go here)
    │  │  │  │  │  │  │  │  │  │  │  │  │  │  │  │
    │  │  │  │  │  │  │  │  │  │  │  │  │  │  │  │
    │  ○  ○  ○  ○  ○  ○  ○  ○  ○  ○  ○  ○  ○  ○ │
    │                                            │
    │ -  -  -  -  -  -  -  -  -  -  -  -  -  -  │  ← Negative rail (GND)
    └────────────────────────────────────────────┘
    
    The middle groove allows chips to straddle across.
    Left side rows connect LEFT, right side rows connect RIGHT.
```

### Push Buttons
```
    Top View:          Side View:
    ┌──────┐           ┌──────┐
    │ ○  ○ │           │      │ ← Two legs on each side
    │      │           │  ──  │ ← Button mechanism
    │ ○  ○ │           │      │
    └──────┘           └──────┘
    
    When pressed, ALL FOUR legs connect together.
```

### Resistors (10kΩ)
```
    Identifying 10kΩ resistors:
    Color bands: BROWN ─ BLACK ─ ORANGE ─ GOLD
    
    |-----|-----|
    ↓     ↓     ↓
    Brown Black Orange Gold
    |     |     |
    1     0     ×1000 = 10,000Ω = 10kΩ
```

---

# 3. UNDERSTANDING YOUR GPIO PINS

## Your Board Pin Layout (Left Side)

```
    LEFT SIDE (top to bottom):
    ═════════════════════════════════════════════
    
    [BOOT]    ← Reset into flash mode
    3V3        ← 3.3V power OUTPUT (don't connect power here!)
    GND        ← Ground connection
    D15 ←      ← WE WILL USE THIS (GPIO 15)
    D2  ←      ← WE WILL USE THIS - Built-in LED (GPIO 2)
    D4  ←      ← WE WILL USE THIS (GPIO 4)
    RX2        ← Serial receive 2
    TX2        ← Serial transmit 2
    D5  ←      ← WE WILL USE THIS (GPIO 5)
    D18 ←      ← WE WILL USE THIS (GPIO 18)
    D19 ←      ← WE WILL USE THIS (GPIO 19)
    D21 ←      ← WE WILL USE THIS (GPIO 21)
    RX0        ← Serial receive 0 (USB)
    TX0        ← Serial transmit 0 (USB)
    D22 ←      ← WE WILL USE THIS (GPIO 22)
    D23 ←      ← WE WILL USE THIS (GPIO 23)
```

## Your Board Pin Layout (Right Side)

```
    RIGHT SIDE (top to bottom):
    ═════════════════════════════════════════════
    
    VIN         ← 5V input (from USB)
    GND         ← Ground connection
    D13 ←       ← WE WILL USE THIS (GPIO 13)
    D12         ← Boot strap pin (avoid if possible)
    D14 ←       ← WE WILL USE THIS (GPIO 14)
    D27         ← WE WILL USE THIS (GPIO 27)
    D26 ←       ← WE WILL USE THIS (GPIO 26)
    D25 ←       ← WE WILL USE THIS (GPIO 25)
    D33         ← Analog input only
    D32         ← Analog input (but can be digital)
    D35         ← INPUT ONLY! (GPIO 35)
    D34         ← INPUT ONLY! (GPIO 34)
    VN          ← INPUT ONLY! (GPIO 39)
    VP          ← INPUT ONLY! (GPIO 36)
    [EN]        ← Reset button
```

## Pin Categories

### ✅ SAFE TO USE FOR YOUR PROJECT

```
ROW PINS (OUTPUT):
    D4 (GPIO 4)
    D5 (GPIO 5)
    D14 (GPIO 14)
    D18 (GPIO 18)
    D19 (GPIO 19)

COLUMN PINS (INPUT):
    D13 (GPIO 13)
    D21 (GPIO 21)
    D22 (GPIO 22)
    D23 (GPIO 23)
    D25 (GPIO 25)
    D26 (GPIO 26)

STATUS PINS:
    D2 (GPIO 2)  - Built-in LED
    D15 (GPIO 15) - Red LED
    D27 (GPIO 27) - Buzzer
```

### ❌ NEVER USE (Flash Memory)

```
D6  (GPIO 6)  - Flash clock
D7  (GPIO 7)  - Flash data
D8  (GPIO 8)  - Flash data
D9  (GPIO 9)  - Flash data
D10 (GPIO 10) - Flash data
D11 (GPIO 11) - Flash data
```

### ⚠️ USE WITH CAUTION

```
D12 (GPIO 12) - Boot strap (affects voltage during boot)
D2  (GPIO 2)  - Boot strap (but OK for LED)
D0  (GPIO 0)  - Boot mode (but not on your board header)
```

### 🔒 INPUT ONLY

```
D35 (GPIO 35) - Analog only
D34 (GPIO 34) - Analog only
VN  (GPIO 39) - Analog only
VP  (GPIO 36) - Analog only
D32 (GPIO 32) - Analog capable but can use as digital
D33 (GPIO 33) - Analog capable but can use as digital
```

---

# 4. WHY USE A MATRIX DESIGN?

## The Problem

You want to connect 30 buttons, but you only have about 16 usable GPIO pins.

## The Solution: 5×6 Matrix

```
┌─────────────────────────────────────────────────────────────────────────┐
│                                                                         │
│                        MATRIX DESIGN (5 ROWS × 6 COLUMNS)              │
│                                                                         │
│        COL0    COL1    COL2    COL3    COL4    COL5                     │
│          │       │       │       │       │       │                      │
│    ROW 0 ┼───────┼───────┼───────┼───────┼───────┼───────→ D4 (GPIO 4) │
│          │       │       │       │       │       │                     │
│    ROW 1 ┼───────┼───────┼───────┼───────┼───────┼───────→ D5 (GPIO 5) │
│          │       │       │       │       │       │                     │
│    ROW 2 ┼───────┼───────┼───────┼───────┼───────┼───────→ D14(GPIO14) │
│          │       │       │       │       │       │                     │
│    ROW 3 ┼───────┼───────┼───────┼───────┼───────┼───────→ D18(GPIO18) │
│          │       │       │       │       │       │                     │
│    ROW 4 ┼───────┼───────┼───────┼───────┼───────┼───────→ D19(GPIO19) │
│                                                                         │
│          ↑       ↑       ↑       ↑       ↑       ↑                      │
│          │       │       │       │       │       │                      │
│        D13      D21      D22     D23     D25     D26                     │
│        (GPIO13)(GPIO21)(GPIO22)(GPIO23)(GPIO25)(GPIO26)                 │
│                                                                         │
│    Total pins used: 5 (rows) + 6 (columns) = 11 pins for 30 buttons!  │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

## How It Works

```
STEP 1: Drive ROW 0 (D4) = LOW, others = HIGH
┌────────────────────────────────────────────────────┐
│                                                    │
│   D4=LOW   D5=HIGH  D14=HIGH D18=HIGH D19=HIGH   │
│     ↓                                              │
│   Row 0 is "scanning"                              │
│                                                    │
│   If button at (Row 0, Col 3) is pressed:         │
│   → Current flows: D4 → Button → Col 3 → D23     │
│   → D23 reads LOW → Button detected!             │
│                                                    │
└────────────────────────────────────────────────────┘

STEP 2: Drive ROW 1 (D5) = LOW, others = HIGH
┌────────────────────────────────────────────────────┐
│                                                    │
│   D4=HIGH  D5=LOW   D14=HIGH D18=HIGH D19=HIGH   │
│     ↓                                              │
│   Row 1 is "scanning"                              │
│                                                    │
│   If button at (Row 1, Col 0) is pressed:         │
│   → Current flows: D5 → Button → Col 0 → D13     │
│   → D13 reads LOW → Button 6 detected!           │
│                                                    │
└────────────────────────────────────────────────────┘

Continue for all 5 rows...
```

---

# 5. CORRECT PIN MAPPING

## Complete Pin Assignment for ESP32 DevKit V1 (DOIT)

```
╔═══════════════════════════════════════════════════════════════════════════╗
║                     PIN MAPPING - YOUR BOARD                               ║
╠═══════════════════════════════════════════════════════════════════════════╣
║                                                                           ║
║   ROW PINS (OUTPUT - Drive LOW when scanning):                           ║
║   ──────────────────────────────────────────────────────────────────────── ║
║   D4  (GPIO 4)  ──────────────→ ROW 0 ─→ Buttons 0, 1, 2, 3, 4, 5       ║
║   D5  (GPIO 5)  ──────────────→ ROW 1 ─→ Buttons 6, 7, 8, 9, 10, 11     ║
║   D14 (GPIO 14) ──────────────→ ROW 2 ─→ Buttons 12,13,14,15,16,17     ║
║   D18 (GPIO 18) ──────────────→ ROW 3 ─→ Buttons 18,19,20,21,22,23     ║
║   D19 (GPIO 19) ──────────────→ ROW 4 ─→ Buttons 24,25,26,27,28,29     ║
║                                                                           ║
║   COLUMN PINS (INPUT_PULLUP - Detect button press):                     ║
║   ──────────────────────────────────────────────────────────────────────── ║
║   D13 (GPIO 13) ←────────────── COL 0 ─→ Buttons 0, 6,12,18,24          ║
║   D21 (GPIO 21) ←────────────── COL 1 ─→ Buttons 1, 7,13,19,25          ║
║   D22 (GPIO 22) ←────────────── COL 2 ─→ Buttons 2, 8,14,20,26          ║
║   D23 (GPIO 23) ←────────────── COL 3 ─→ Buttons 3, 9,15,21,27          ║
║   D25 (GPIO 25) ←────────────── COL 4 ─→ Buttons 4,10,16,22,28          ║
║   D26 (GPIO 26) ←────────────── COL 5 ─→ Buttons 5,11,17,23,29          ║
║                                                                           ║
║   STATUS INDICATORS:                                                       ║
║   ──────────────────────────────────────────────────────────────────────── ║
║   D2  (GPIO 2)  ───────────────→ Built-in LED (WiFi status)              ║
║   D15 (GPIO 15) ──220Ω───────→ Red LED (+) ──→ GND                      ║
║   D27 (GPIO 27) ─────────────→ Buzzer (+) ──→ GND                       ║
║                                                                           ║
║   POWER:                                                                   ║
║   ──────────────────────────────────────────────────────────────────────── ║
║   3V3  (3.3V) ───────────────→ (+) Positive rail                        ║
║   GND  (Ground) ──────────────→ (-) Negative rail                        ║
║                                                                           ║
║   PULL-UP RESISTORS (10kΩ):                                               ║
║   ──────────────────────────────────────────────────────────────────────── ║
║   Each column pin needs a 10kΩ resistor to 3.3V rail                     ║
║                                                                           ║
╚═══════════════════════════════════════════════════════════════════════════╝
```

## Button Position Map

```
BUTTON LAYOUT ON BREADBOARD:

         Column  Column  Column  Column  Column  Column
           0       1       2       3       4       5
          D13     D21     D22     D23     D25     D26
           │       │       │       │       │       │
    ROW 0 ┼───────┼───────┼───────┼───────┼───────┼─────── D4
    (D4)  │ [B0]  │ [B1]  │ [B2]  │ [B3]  │ [B4]  │ [B5]   │
          │ S_01  │ S_02  │ S_03  │ S_04  │ S_05  │ S_06   │
          │       │       │       │       │       │        │
    ROW 1 ┼───────┼───────┼───────┼───────┼───────┼─────── D5
    (D5)  │ [B6]  │ [B7]  │ [B8]  │ [B9]  │ [B10] │ [B11]  │
          │ S_07  │ S_08  │ S_09  │ S_10  │ S_11  │ S_12   │
          │       │       │       │       │       │        │
    ROW 2 ┼───────┼───────┼───────┼───────┼───────┼─────── D14
    (D14) │ [B12] │ [B13] │ [B14] │ [B15] │ [B16] │ [B17]  │
          │ S_13  │ S_14  │ S_15  │ S_16  │ S_17  │ S_18   │
          │       │       │       │       │       │        │
    ROW 3 ┼───────┼───────┼───────┼───────┼───────┼─────── D18
    (D18) │ [B18] │ [B19] │ [B20] │ [B21] │ [B22] │ [B23]  │
          │ S_19  │ S_20  │ S_21  │ S_22  │ S_23  │ S_24   │
          │       │       │       │       │       │        │
    ROW 4 ┼───────┼───────┼───────┼───────┼───────┼─────── D19
    (D19) │ [B24] │ [B25] │ [B26] │ [B27] │ [B28] │ [B29]  │
          │ S_25  │ S_26  │ S_27  │ S_28  │ S_29  │ S_30   │
          │       │       │       │       │       │        │
```

---

# 6. PHYSICAL WIRING STEP-BY-STEP

## STEP 1: Prepare Your Workspace

**What you need:**
- Clean, well-lit table
- All components in front of you
- Small Phillips screwdriver (optional)

**Action:**
1. Lay out all components
2. Make sure ESP32 is NOT powered (no USB connected)
3. Clear workspace

---

## STEP 2: Place ESP32 on Breadboard

**Action:**
1. Take ESP32 DevKit V1
2. Position it so Micro-USB port faces UP (toward ceiling)
3. Insert ALL pins into the breadboard
4. The ESP32 should straddle the CENTER GROOVE

**Visual:**
```
    ══════════════════════════════════════════════════════════════
                               ↑ USB port faces UP
                               
           ┌─────────────────────────────────────────────┐
           │                                             │
           │                 ESP32                       │
           │                                             │
    ───────┤                                             ├───────
    LEFT   │    ┌─────────────────────────────┐        │ RIGHT
    SIDE   │    │                             │        │ SIDE
           │    │        CENTER GROOVE         │        │
    ───────┤    │       (no contacts here)    │        ├───────
           │    │                             │        │
           │    └─────────────────────────────┘        │
           │                                             │
           └─────────────────────────────────────────────┘
```

---

## STEP 3: Connect Power Rails

**Action:**
1. Connect RED wire from ESP32 **3V3** pin to **positive rail** (+)
2. Connect BLACK wire from ESP32 **GND** pin to **negative rail** (-)

**Where to find pins on ESP32:**
```
LEFT SIDE (top to bottom):
[BOOT] ← don't use
3V3    ← RED wire goes here
GND    ← BLACK wire goes here
D15
D2
D4
RX2
TX2
D5
D18
D19
D21
RX0
TX0
D22
D23
```

**Visual:**
```
    Breadboard
    ╔═══════════════════════════════════════════════════╗
    ║  +  +  +  +  +  +  +  +  +  +  +  +  +  +  +  + ║  (+ Rail - 3.3V)
    ║  │                                              ║
    ║  └──── RED wire from ESP32 3V3                  ║
    ╠═══════════════════════════════════════════════════╣
    ║  ○  ○  ○  ○  ○  ○  ○  ○  ○  ○  ○  ○  ○  ○  ○ ║
    ║  │  │  │  │  │  │  │  │  │  │  │  │  │  │  │  │ ║
    ║  │  │  │  │  │  │  │  │  │  │  │  │  │  │  │  │ ║
    ╠═══════════════════════════════════════════════════╣
    ║  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  ║  (- Rail - GND)
    ║  │                                              ║
    ║  └──── BLACK wire from ESP32 GND                ║
    ╚═══════════════════════════════════════════════════╝
```

---

## STEP 4: Install Pull-Up Resistors (Columns)

**What you need:**
- 6 × 10kΩ resistors (Brown-Black-Orange-Gold)
- 6 × Male-to-Female jumper wires

**Action:**
For each column, do the following:

1. Insert 10kΩ resistor between column bus and (+) rail
2. Connect column GPIO wire to the same column bus

**Detailed for Column 0 (D13):**
```
    3.3V ───[10kΩ]───(+) Rail
                      │
                      ├──→ To Column 0 bus
                      │
    D13 (GPIO 13)──────┘
    
    On breadboard:
    ─────────────────────────────────────────────
    (+) Rail: [One leg of 10kΩ resistor]
                │
                └──[Other leg]──→ Column 0 bus
                                          │
    D13 (GPIO 13) ──── Male-to-Female ────┘
    wire from ESP32
```

**Do this for ALL 6 columns:**
```
Column 0: 10kΩ + D13 (GPIO 13) → Column bus 0
Column 1: 10kΩ + D21 (GPIO 21) → Column bus 1
Column 2: 10kΩ + D22 (GPIO 22) → Column bus 2
Column 3: 10kΩ + D23 (GPIO 23) → Column bus 3
Column 4: 10kΩ + D25 (GPIO 25) → Column bus 4
Column 5: 10kΩ + D26 (GPIO 26) → Column bus 5
```

---

## STEP 5: Wire ROW Pins

**What you need:**
- 5 × Male-to-Female jumper wires

**Action:**
Connect these wires from ESP32 to row bus lines:

```
ESP32          → Breadboard Row Bus
────────────────────────────────────────
D4  (GPIO 4)  ────────────────→ ROW 0 (Buttons 0-5)
D5  (GPIO 5)  ────────────────→ ROW 1 (Buttons 6-11)
D14 (GPIO 14) ────────────────→ ROW 2 (Buttons 12-17)
D18 (GPIO 18) ────────────────→ ROW 3 (Buttons 18-23)
D19 (GPIO 19) ────────────────→ ROW 4 (Buttons 24-29)
```

**On breadboard:**
```
    Row 4 bus ──────────────────────────────── D19
    Row 3 bus ──────────────────────────────── D18
    Row 2 bus ──────────────────────────────── D14
    Row 1 bus ──────────────────────────────── D5
    Row 0 bus ──────────────────────────────── D4
```

---

## STEP 6: Place Buttons

**Action:**
1. Take a button
2. Place it so it STRADDLES the center groove
3. Each button has 4 legs
4. Legs should go into 4 different holes

**Button placement:**
```
    TOP VIEW OF BREADBOARD:
    
    + Rail ────────────────────────────────────── +
    
    Row 4 bus ─[B24]─[B25]─[B26]─[B27]─[B28]─[B29]── Row 4 bus
               │    │    │    │    │    │
    ───────────┴────┴────┴────┴────┴────┴─────────────
               
               [B18]─[B19]─[B20]─[B21]─[B22]─[B23]── Row 3 bus
               │    │    │    │    │    │
    ───────────┴────┴────┴────┴────┴────┴─────────────
               
               [B12]─[B13]─[B14]─[B15]─[B16]─[B17]── Row 2 bus
               │    │    │    │    │    │
    ───────────┴────┴────┴────┴────┴────┴─────────────
               
               [B6]───[B7]───[B8]───[B9]───[B10]─[B11]── Row 1 bus
               │    │    │    │    │    │
    ───────────┴────┴────┴────┴────┴────┴─────────────
               
               [B0]───[B1]───[B2]───[B3]───[B4]───[B5]── Row 0 bus
               
    - Rail ────────────────────────────────────── -
    
         Col0   Col1   Col2   Col3   Col4   Col5
         D13    D21    D22    D23    D25    D26
```

---

## STEP 7: Wire Buttons to Matrix

**For each button, connect 2 legs:**

### Connection Type 1: Top 2 legs → Row bus
- Connect top-left leg to row bus (left side)
- Connect top-right leg to row bus (right side)
- OR: Use one row bus line for entire row

### Connection Type 2: Bottom 2 legs → Column bus
- Connect bottom-left leg to column bus
- Connect bottom-right leg to column bus

**Easier method: Use continuous rows**
```
For ROW 0 (Buttons 0-5):
- Take ONE wire from Row 0 bus → connect to LEFT leg of B0
- Take ONE wire from Row 0 bus → connect to LEFT leg of B1
- Take ONE wire from Row 0 bus → connect to LEFT leg of B2
- ...continue for all buttons in row

For COLUMN 0 (Buttons 0, 6, 12, 18, 24):
- Take ONE wire from Col 0 bus → connect to RIGHT leg of B0
- Take ONE wire from Col 0 bus → connect to RIGHT leg of B6
- Take ONE wire from Col 0 bus → connect to RIGHT leg of B12
- ...continue for all buttons in column
```

---

## STEP 8: Connect Status LEDs

**Action:**
1. Insert Red LED into breadboard
2. Long leg (+) → D15 through 220Ω resistor
3. Short leg (-) → GND rail

**LED Connection:**
```
    D15 (GPIO 15) ──[220Ω]──→ Long leg of Red LED
                                      │
                                      ↓
                                     Short leg
                                      │
                                      ↓
                                    GND rail
```

---

## STEP 9: Connect Buzzer

**Action:**
1. Insert buzzer into breadboard
2. Long leg (+) → D27
3. Short leg (-) → GND rail

**Buzzer Connection:**
```
    D27 (GPIO 27) ─────────────────→ Long leg of Buzzer
                                        │
                                        ↓
                                       Short leg
                                        │
                                        ↓
                                      GND rail
```

---

## STEP 10: Final Check

**Before powering on, verify:**

```
✓ 3V3 connected to (+) rail
✓ GND connected to (-) rail
✓ 6 pull-up resistors (10kΩ) from columns to (+) rail
✓ 5 row wires: D4, D5, D14, D18, D19
✓ 6 column wires: D13, D21, D22, D23, D25, D26
✓ Red LED: D15 → 220Ω → LED+ → GND
✓ Buzzer: D27 → LED+ → GND
✓ All buttons inserted properly (straddling center groove)
```

---

# 7. CIRCUIT EXPLANATION

## How Button Press Detection Works

### The Principle

```
NORMAL STATE (button NOT pressed):
┌─────────────────────────────────────────────┐
│                                             │
│   3.3V ──[10kΩ]──(+)Rail                    │
│                      │                      │
│                      ├──→ Column Bus        │
│                      │         │            │
│                     GND       [Button]       │
│                      │         │            │
│                     D13 ◄─────┘            │
│                    (reads HIGH)             │
│                                             │
│   Result: Column pin reads HIGH              │
│                                             │
└─────────────────────────────────────────────┘

PRESSED STATE (button pressed):
┌─────────────────────────────────────────────┐
│                                             │
│   3.3V ──[10kΩ]──(+)Rail                    │
│                      │                      │
│                      ├──→ Column Bus        │
│                      │         │            │
│                     D13 ◄─────[Button]──────┼──→ Row bus (LOW)
│                    (reads LOW)   │          │
│                                  │          │
│                                 GND         │
│                                             │
│   Result: Column pin reads LOW = pressed!   │
│                                             │
└─────────────────────────────────────────────┘
```

## Matrix Scanning Logic

```
The ESP32 scans row by row:

1. Set ALL rows HIGH (idle)
2. Set ROW 0 (D4) = LOW
3. Wait 100 microseconds (settling time)
4. Read all columns:
   - D13 = LOW? → Button 0 pressed!
   - D21 = LOW? → Button 1 pressed!
   - D22 = LOW? → Button 2 pressed!
   - ...etc
5. Set ROW 0 = HIGH
6. Set ROW 1 (D5) = LOW
7. Repeat reading columns
8. ...continue for all 5 rows
9. Repeat forever
```

## Debouncing Explained

```
WITHOUT DEBOUNCE:
┌────────────────────────────────────────────┐
│ Button pressed:                            │
│                                            │
│ Pin ──┐                                    │
│       │   │   │    │                       │
│       └───┘   └────┘   (unstable)         │
│                                            │
│ Might detect: 1, 0, 1, 1, 0, 1, 1...     │
│ (Multiple false triggers!)                  │
└────────────────────────────────────────────┘

WITH DEBOUNCE (50ms):
┌────────────────────────────────────────────┐
│ Button pressed:                            │
│                                            │
│ Pin ──┐                                    │
│       │█████████████ (stable HIGH)         │
│       └───┘████████│                       │
│                  │                         │
│                  └─ Only detects ONE press  │
│                     after stable for 50ms  │
│                                            │
└────────────────────────────────────────────┘
```

---

# 8. COMPLETE ESP32 CODE

## File 1: config.h

Create this file in your Arduino IDE sketch folder:

```cpp
/*
  ESP32 Configuration File
  For ESP32 DevKit V1 (DOIT)
*/

#ifndef CONFIG_H
#define CONFIG_H

// ========================================
// WIFI CREDENTIALS - EDIT THESE!
// ========================================

#define WIFI_SSID "YOUR_WIFI_NAME"
#define WIFI_PASSWORD "YOUR_WIFI_PASSWORD"

// ========================================
// API SERVER - EDIT THIS!
// ========================================

// Your PC's IP address
#define API_HOST "http://192.168.1.100:5000"

// ========================================
// DEVICE IDENTIFICATION
// ========================================

#define DEVICE_ID "ESP32-001"
#define DEVICE_LOCATION "Smart Evacuation Floor 1"

#endif // CONFIG_H
```

## File 2: esp32_emergency_controller.ino

See the file in: `esp32/firmware/esp32_emergency_controller/esp32_emergency_controller.ino`

### Key Pin Assignments

```cpp
// ROW pins (OUTPUT) - LEFT side of board
const int ROW_PINS[ROWS] = {
    4,    // D4  → Row 0
    5,    // D5  → Row 1
    14,   // D14 → Row 2
    18,   // D18 → Row 3
    19    // D19 → Row 4
};

// COLUMN pins (INPUT_PULLUP) - RIGHT side of board
const int COL_PINS[COLS] = {
    13,   // D13 → Column 0
    21,   // D21 → Column 1
    22,   // D22 → Column 2
    23,   // D23 → Column 3
    25,   // D25 → Column 4
    26    // D26 → Column 5
};

// Status indicators
const int LED_BUILTIN = 2;     // D2  → Built-in LED
const int LED_RED = 15;         // D15 → Red LED
const int BUZZER_PIN = 27;      // D27 → Buzzer
```

---

# 9. IOT INTEGRATION EXPLAINED

## Data Flow

```
┌────────────────────────────────────────────────────────────────────────┐
│                                                                        │
│   ESP32 (Arduino)                      FLASK SERVER (Python)         │
│   ┌──────────────────┐                  ┌──────────────────┐          │
│   │                  │    HTTP POST     │                  │          │
│   │  Button Press!   │ ──────────────→ │  /sensor-update │          │
│   │                  │                  │                  │          │
│   │  Create JSON:   │    WiFi          │  Parse JSON:    │          │
│   │  {               │ ──────────────→ │  sensor_id      │          │
│   │    sensor_id,    │                  │  type: FIRE     │          │
│   │    type: FIRE   │                  │                  │          │
│   │  }              │                  │  Save to memory │          │
│   │                  │                  │                  │          │
│   │  Success!       │ ←────────────── │  Return: OK     │          │
│   └──────────────────┘                  └──────────────────┘          │
│                                                                        │
└────────────────────────────────────────────────────────────────────────┘
```

## JSON Format

### ESP32 Sends:
```json
{
    "sensor_id": "S_01",
    "type": "FIRE",
    "device_id": "ESP32-001",
    "source": "esp32"
}
```

### Flask Receives:
```python
sensor_id = request.json['sensor_id']
emergency_type = request.json['type']
```

---

# 10. FLASK BACKEND SETUP

## Your Backend Already Supports ESP32!

Your file `backend/app.py` already has these endpoints:

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/esp32/register` | POST | Register ESP32 device |
| `/esp32/heartbeat` | POST | Health check from ESP32 |
| `/sensor-update` | POST | Receive emergency alert |
| `/sensor-status` | GET | Get active alerts |

## Steps to Connect

### Step 1: Find Your PC IP Address

**Windows:**
```
1. Press Win + R
2. Type "cmd", press Enter
3. Type: ipconfig
4. Look for "IPv4 Address"
   Example: 192.168.1.100
```

### Step 2: Update config.h

```cpp
#define WIFI_SSID "YourWiFiName"
#define WIFI_PASSWORD "YourWiFiPassword"
#define API_HOST "http://192.168.1.100:5000"  // Use your PC's IP!
```

### Step 3: Start Flask

```bash
cd backend
python app.py
```

### Step 4: Test

Open browser to: `http://localhost:5000/api`

---

# 11. TESTING PROCEDURES

## Test 1: Initial Power-On

**Steps:**
1. Connect ESP32 to computer via Micro-USB
2. Open Arduino IDE Serial Monitor (115200 baud)
3. Press EN button on ESP32

**Expected Output:**
```
╔═══════════════════════════════════════════════════════════════╗
║   ESP32 SMART EVACUATION CONTROLLER v2.1                     ║
║   30-Button Emergency Matrix + WiFi                          ║
╚═══════════════════════════════════════════════════════════════╝

Initializing 5x6 button matrix...
  LEFT side: D4, D5, D14, D18, D19 = ROWS
  RIGHT side: D13, D21, D22, D23, D25, D26 = COLUMNS

  ROW 0 → D4 (GPIO 4)
  ROW 1 → D5 (GPIO 5)
  ...

WiFi Connected!
IP Address: 192.168.1.101
```

## Test 2: Press Each Button

**Steps:**
1. Press Button 0 (top-left)
2. Watch Serial Monitor
3. Press Button 5, 6, 11, 12, 29, etc.

**Expected Output:**
```
========================================
  EMERGENCY TRIGGERED!
========================================
  Button #: 0 (C1A-North)
  Sensor ID: S_01
  Type: FIRE
========================================
```

## Test 3: Verify Flask Receives

**Steps:**
1. Press a button
2. Open browser to `http://localhost:5000/sensor-status`

**Expected:**
```json
{
  "active_emergencies": [
    {
      "sensor_id": "S_01",
      "type": "FIRE",
      ...
    }
  ],
  "total_active": 1
}
```

---

# 12. COMMON MISTAKES & SOLUTIONS

## Problem: WiFi Won't Connect

**Check:**
- SSID and password correct?
- WiFi is 2.4GHz (not 5GHz)?
- ESP32 close enough to router?

## Problem: Button Not Detected

**Check:**
- Pull-up resistor (10kΩ) connected to that column?
- Button legs making contact?
- Row wire connected to correct pin?

## Problem: Multiple Buttons Trigger at Once

**Check:**
- Short circuit between columns?
- Button legs touching each other?
- Solder bridges on perfboard?

## Problem: ESP32 Not Recognized

**Check:**
- USB cable is data-capable (not charge-only)?
- CP2102 drivers installed?
- Correct COM port selected?

## Problem: Wrong Button Numbers

**Check:**
- Row wiring in order: D4, D5, D14, D18, D19
- Column wiring in order: D13, D21, D22, D23, D25, D26
- Buttons properly placed on breadboard?

---

# 13. COMPLETE WORKING FLOW

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                                                                             │
│  STEP 1: USER presses Button 0 (S_01)                                      │
│  ════════════════════════════════════                                      │
│                                                                             │
│       [B0] ← Pressed!                                                      │
│        │                                                                   │
│        ↓                                                                   │
│  ┌─────┴─────┐                                                             │
│  │           │                                                             │
│  │ ROW 0 bus │ ← D4 (GPIO 4) = LOW                                        │
│  │           │                                                             │
│  └─────┬─────┘                                                             │
│        │                                                                   │
│        └────────→ COL 0 bus → D13 (GPIO 13) = LOW ✓ Button detected!      │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                                                                             │
│  STEP 2: ESP32 Processes                                                   │
│  ═══════════════════════════                                               │
│                                                                             │
│  • Debounce check (50ms) ✓                                                 │
│  • Cycle type: FIRE → SMOKE                                                 │
│  • Create JSON payload                                                     │
│  • Flash red LED + beep buzzer                                             │
│  • Increment counter                                                       │
│                                                                             │
│  Payload:                                                                   │
│  { "sensor_id": "S_01", "type": "FIRE", "device_id": "ESP32-001" }        │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                                                                             │
│  STEP 3: WiFi Transmission                                                  │
│  ════════════════════                                                       │
│                                                                             │
│  ┌──────────────┐     WiFi      ┌──────────────┐                           │
│  │   ESP32      │ ────────────→ │   Router     │                           │
│  │              │   HTTP POST   │              │                           │
│  │ 192.168.1.101│              │ 192.168.1.1  │                           │
│  └──────────────┘              └──────┬───────┘                           │
│                                        │                                    │
│                                        │ LAN                                │
│                                        ▼                                    │
│                                  ┌──────────────┐                           │
│                                  │   Computer   │                           │
│                                  │ 192.168.1.100│ ← Flask server           │
│                                  └──────────────┘                           │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                                                                             │
│  STEP 4: Flask Processes                                                    │
│  ════════════════════                                                       │
│                                                                             │
│  • Receives POST at /sensor-update                                         │
│  • Parses JSON                                                              │
│  • Stores in active_emergencies list                                        │
│  • Returns: {"status": "updated"}                                          │
│                                                                             │
│  Storage:                                                                   │
│  active_emergencies = [                                                     │
│      {sensor_id: "S_01", type: "FIRE", location: "...", ...}             │
│  ]                                                                           │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                                                                             │
│  STEP 5: Frontend Updates                                                   │
│  ══════════════════                                                         │
│                                                                             │
│  • Frontend polls /sensor-status every few seconds                         │
│  • Or: Frontend receives WebSocket update                                   │
│  • Dashboard shows alert on map at S_01 location                          │
│  • Shows evacuation path avoiding S_01                                     │
│                                                                             │
│  ┌─────────────────────────────────────────────────────┐                   │
│  │           SMART EVACUATION DASHBOARD                 │                   │
│  │                                                      │                   │
│  │    Building Map                                       │                   │
│  │    ┌──────────┐                                      │                   │
│  │    │ [S_01] 🔴│ ← FIRE alert at S_01!               │                   │
│  │    │  FIRE!   │                                      │                   │
│  │    └──────────┘                                      │                   │
│  │                                                      │                   │
│  │    Route: [Room] ───→ [EXIT]                         │                   │
│  │                                                      │                   │
│  └─────────────────────────────────────────────────────┘                   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Timeline

| Step | Action | Time |
|------|--------|------|
| 0ms | User presses button | T+0 |
| 1ms | ESP32 detects | T+1 |
| 50ms | Debounce confirms | T+50 |
| 52ms | JSON created | T+52 |
| 100ms | WiFi sends | T+100 |
| 200ms | Flask receives | T+200 |
| 300ms | Database updated | T+300 |
| 500ms | Frontend shows | T+500 |

**Total: ~500ms (0.5 seconds)**

---

# QUICK REFERENCE CARD

```
╔═══════════════════════════════════════════════════════════════════════════╗
║                       ESP32 DEVKIT V1 (DOIT) QUICK REFERENCE             ║
╠═══════════════════════════════════════════════════════════════════════════╣
║                                                                           ║
║   PINS TO USE:                                                            ║
║   ───────────────                                                         ║
║   ROWS (Output):  D4, D5, D14, D18, D19                                  ║
║   COLS (Input):   D13, D21, D22, D23, D25, D26                           ║
║   STATUS:         D2 (LED), D15 (LED), D27 (Buzzer)                      ║
║   POWER:          3V3 (+), GND (-)                                        ║
║                                                                           ║
║   PINS TO AVOID:                                                          ║
║   ───────────────                                                         ║
║   D6, D7, D8, D9, D10, D11 = Flash memory (NEVER USE!)                  ║
║   D35, D34, VN, VP = Input only                                          ║
║                                                                           ║
║   PULL-UP RESISTORS:                                                      ║
║   ───────────────────                                                     ║
║   10kΩ from each column pin to 3.3V                                      ║
║   (Brown-Black-Orange-Gold)                                               ║
║                                                                           ║
║   LED RESISTORS:                                                          ║
║   ───────────────                                                         ║
║   220Ω from D15 to Red LED (+)                                           ║
║   (Red-Red-Brown-Gold)                                                   ║
║                                                                           ║
║   BUTTON MATRIX:                                                          ║
║   ───────────────                                                         ║
║   5 rows × 6 columns = 30 buttons                                        ║
║   Total pins needed: 11 (5 rows + 6 columns)                              ║
║                                                                           ║
║   BUTTON TO SENSOR MAP:                                                   ║
║   ────────────────────                                                    ║
║   B0-5   → S_01 to S_06    (Row 0, D4)                                  ║
║   B6-11  → S_07 to S_12    (Row 1, D5)                                  ║
║   B12-17 → S_13 to S_18    (Row 2, D14)                                 ║
║   B18-23 → S_19 to S_24    (Row 3, D18)                                 ║
║   B24-29 → S_25 to S_30    (Row 4, D19)                                 ║
║                                                                           ║
╚═══════════════════════════════════════════════════════════════════════════╝
```

---

**Good luck with your Smart Evacuation System!**
