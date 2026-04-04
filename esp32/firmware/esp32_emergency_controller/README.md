# ESP32 Smart Evacuation Controller

## Version 2.1 - For ESP32 DevKit V1 (DOIT)

> **Board Details:**
> - Micro-USB on top
> - BOOT button on LEFT
> - EN (Reset) button on RIGHT

---

## Quick Setup

### 1. Edit Configuration

Edit `config.h` with your settings:

```cpp
#define WIFI_SSID "YourWiFiName"
#define WIFI_PASSWORD "YourWiFiPassword"
#define API_HOST "http://192.168.1.100:5000"
#define DEVICE_ID "ESP32-001"
```

### 2. Wire the Hardware

**Pin Assignment for ESP32 DevKit V1 (DOIT):**

```
ROW PINS (OUTPUT) - LEFT side of board:
─────────────────────────────────────────────────────────────
D4  (GPIO 4)  → Row 0 → Buttons 0, 1, 2, 3, 4, 5
D5  (GPIO 5)  → Row 1 → Buttons 6, 7, 8, 9, 10, 11
D14 (GPIO 14) → Row 2 → Buttons 12, 13, 14, 15, 16, 17
D18 (GPIO 18) → Row 3 → Buttons 18, 19, 20, 21, 22, 23
D19 (GPIO 19) → Row 4 → Buttons 24, 25, 26, 27, 28, 29

COLUMN PINS (INPUT_PULLUP) - RIGHT side of board:
─────────────────────────────────────────────────────────────
D13 (GPIO 13) ← Column 0 ← Buttons 0, 6, 12, 18, 24
D21 (GPIO 21) ← Column 1 ← Buttons 1, 7, 13, 19, 25
D22 (GPIO 22) ← Column 2 ← Buttons 2, 8, 14, 20, 26
D23 (GPIO 23) ← Column 3 ← Buttons 3, 9, 15, 21, 27
D25 (GPIO 25) ← Column 4 ← Buttons 4, 10, 16, 22, 28
D26 (GPIO 26) ← Column 5 ← Buttons 5, 11, 17, 23, 29

STATUS INDICATORS:
─────────────────────────────────────────────────────────────
D2  (GPIO 2)  → Built-in LED (WiFi status)
D15 (GPIO 15) → Red LED (Emergency indicator)
D27 (GPIO 27) → Buzzer (Audio alert)

POWER:
─────────────────────────────────────────────────────────────
3V3 → (+) Positive rail (3.3V)
GND → (-) Negative rail (GND)

PULL-UP RESISTORS (10kΩ):
─────────────────────────────────────────────────────────────
Each column pin needs 10kΩ resistor to 3.3V rail
```

### 3. Avoid These Pins

```
D6, D7, D8, D9, D10, D11 → Flash memory (NEVER USE!)
D35, D34, VN, VP → Input only (no output)
```

### 4. Upload to ESP32

1. Open `esp32_emergency_controller.ino` in Arduino IDE
2. Select Tools > Board > ESP32 Dev Module
3. Select correct COM port
4. Click Upload

### 5. Monitor Serial Output

1. Open Serial Monitor (115200 baud)
2. Press EN button on ESP32
3. You should see startup banner and WiFi connection

---

## Button Layout

```
         Col0   Col1   Col2   Col3   Col4   Col5
         D13    D21    D22    D23    D25    D26
          │      │      │      │      │      │
    ROW 0 ┼──────┼──────┼──────┼──────┼──────┼─────── D4
    (D4)  │ [B0] │ [B1] │ [B2] │ [B3] │ [B4] │ [B5]   │
          │ S_01 │ S_02 │ S_03 │ S_04 │ S_05 │ S_06   │
          │      │      │      │      │      │        │
    ROW 1 ┼──────┼──────┼──────┼──────┼──────┼─────── D5
    (D5)  │ [B6] │ [B7] │ [B8] │ [B9] │ [B10]│ [B11]  │
          │ S_07 │ S_08 │ S_09 │ S_10 │ S_11 │ S_12   │
          │      │      │      │      │      │        │
    ROW 2 ┼──────┼──────┼──────┼──────┼──────┼─────── D14
    (D14) │ [B12]│ [B13]│ [B14]│ [B15]│ [B16]│ [B17]  │
          │ S_13 │ S_14 │ S_15 │ S_16 │ S_17 │ S_18   │
          │      │      │      │      │      │        │
    ROW 3 ┼──────┼──────┼──────┼──────┼──────┼─────── D18
    (D18) │ [B18]│ [B19]│ [B20]│ [B21]│ [B22]│ [B23]  │
          │ S_19 │ S_20 │ S_21 │ S_22 │ S_23 │ S_24   │
          │      │      │      │      │      │        │
    ROW 4 ┼──────┼──────┼──────┼──────┼──────┼─────── D19
    (D19) │ [B24]│ [B25]│ [B26]│ [B27]│ [B28]│ [B29]  │
          │ S_25 │ S_26 │ S_27 │ S_28 │ S_29 │ S_30   │
```

---

## Emergency Types

Each press cycles through: FIRE → SMOKE → GAS → BLOCKAGE → CROWD → FIRE

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| WiFi won't connect | Check SSID/password; ensure 2.4GHz WiFi |
| Buttons not detected | Verify wiring; check 10kΩ pull-up resistors |
| API errors | Verify Flask running; check IP address |
| ESP32 not detected | Use data-capable USB cable; install CP2102 drivers |
| Wrong button numbers | Verify row pins: D4,D5,D14,D18,D19; col pins: D13,D21,D22,D23,D25,D26 |

---

## For Detailed Guide

See: `docs/COMPLETE_ESP32_BEGINNER_GUIDE.md`

---

**Version: 2.1 - ESP32 DevKit V1 (DOIT)**
