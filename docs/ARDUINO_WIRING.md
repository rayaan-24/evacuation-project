# Arduino Wiring Guide

## Complete Pin Mapping

### Arduino Uno Pin Layout

```
                        USB
    ┌─────────────────────────────────────┐
    │  1  [TX] [RX] [RST] [3.3V] [5V]   │
    │  2  [GND] [GND] [AREF] [SDA]      │
    │  3  [A0 ] [A1 ] [A2 ] [A3 ] [A4] │
    │  4  [A5 ] [SCL] [13 ] [12 ] [11] │
    │  5  [10 ] [9  ] [8  ] [7  ] [6  ] │
    │  6  [5  ] [4  ] [3  ] [2  ] [1  ] │
    └─────────────────────────────────────┘
```

## Pin Assignments

### Button Matrix

| Arduino Pin | Direction | Connected To |
|-------------|-----------|--------------|
| 2 | OUTPUT | Row 0 (Buttons 0,1,2,3,4) |
| 3 | OUTPUT | Row 1 (Buttons 5,6,7,8,9) |
| 4 | OUTPUT | Row 2 (Buttons 10,11,12,13,14) |
| 5 | OUTPUT | Row 3 (Buttons 15,16,17,18,19) |
| 6 | OUTPUT | Row 4 (Buttons 20,21,22,23,24) |
| 7 | INPUT_PULLUP | Column 0 (Buttons 0,5,10,15,20) |
| 8 | INPUT_PULLUP | Column 1 (Buttons 1,6,11,16,21) |
| 9 | INPUT_PULLUP | Column 2 (Buttons 2,7,12,17,22) |
| 10 | INPUT_PULLUP | Column 3 (Buttons 3,8,13,18,23) |
| 11 | INPUT_PULLUP | Column 4 (Buttons 4,9,14,19,24) |
| 12 | INPUT_PULLUP | Column 5 (Buttons 25,26,27,28,29) |

### Status LEDs

| Arduino Pin | LED Color | Purpose |
|-------------|-----------|---------|
| A1 | Green | System OK indicator |
| A2 | Yellow | Warning/Active emergency |
| A3 | Red | Critical emergency alert |

### Buzzer

| Arduino Pin | Component | Purpose |
|-------------|-----------|---------|
| A0 | Active Buzzer (+) | Audio alerts |

### LCD Display (I2C)

| Arduino Pin | LCD Adapter | Purpose |
|------------|------------|---------|
| A4 (SDA) | SDA | I2C Data |
| A5 (SCL) | SCL | I2C Clock |
| 5V | VCC | Power |
| GND | GND | Ground |

---

## Button Matrix Layout

### Physical Arrangement

```
        COL0    COL1    COL2    COL3    COL4    COL5
       ┌──────┬──────┬──────┬──────┬──────┬──────┐
 ROW0  │  B0  │  B1  │  B2  │  B3  │  B4  │  B5  │  → Pin 2
       ├──────┼──────┼──────┼──────┼──────┼──────┤
 ROW1  │  B6  │  B7  │  B8  │  B9  │ B10  │ B11  │  → Pin 3
       ├──────┼──────┼──────┼──────┼──────┼──────┤
 ROW2  │ B12  │ B13  │ B14  │ B15  │ B16  │ B17  │  → Pin 4
       ├──────┼──────┼──────┼──────┼──────┼──────┤
 ROW3  │ B18  │ B19  │ B20  │ B21  │ B22  │ B23  │  → Pin 5
       ├──────┼──────┼──────┼──────┼──────┼──────┤
 ROW4  │ B24  │ B25  │ B26  │ B27  │ B28  │ B29  │  → Pin 6
       └──────┴──────┴──────┴──────┴──────┴──────┘
        ↓       ↓       ↓       ↓       ↓       ↓
      Pin 7   Pin 8   Pin 9  Pin 10  Pin 11  Pin 12
```

### Button to Sensor Mapping

| Button | Sensor ID | Corridor |
|--------|-----------|----------|
| B0 | sensor_0 | C1A |
| B1 | sensor_1 | C1B |
| B2 | sensor_2 | C1C |
| B3 | sensor_3 | C1D |
| B4 | sensor_4 | C2A |
| B5 | sensor_5 | C2B |
| B6 | sensor_6 | C2C |
| B7 | sensor_7 | C2D |
| B8 | sensor_8 | C3A |
| B9 | sensor_9 | C3B |
| B10 | sensor_10 | C3C |
| B11 | sensor_11 | C3D |
| B12 | sensor_12 | C4A |
| B13 | sensor_13 | C4B |
| B14 | sensor_14 | C5A |
| B15 | sensor_15 | C5B |
| B16 | sensor_16 | C6A |
| B17 | sensor_17 | C6B |
| B18 | sensor_18 | CJ_NW |
| B19 | sensor_19 | CJ_NC |
| B20 | sensor_20 | CJ_NE |
| B21 | sensor_21 | CJ_MW |
| B22 | sensor_22 | CJ_MC |
| B23 | sensor_23 | CJ_ME |
| B24 | sensor_24 | CJ_SW |
| B25 | sensor_25 | CJ_SC |
| B26 | sensor_26 | CJ_SE |
| B27 | sensor_27 | C7A |
| B28 | sensor_28 | C7B |
| B29 | sensor_29 | C7C |

---

## Circuit Diagram (Text)

### Button Matrix

```
Arduino                          Button Matrix
────────                         ─────────────
    ┌─────┐                         
    │ 2   │──────[ROW0]─────┬─┬─┬─┬─┬─┐
    │ 3   │──────[ROW1]─────┼─┼─┼─┼─┼─┤
    │ 4   │──────[ROW2]─────┼─┼─┼─┼─┼─┤
    │ 5   │──────[ROW3]─────┼─┼─┼─┼─┼─┤
    │ 6   │──────[ROW4]─────┴─┴─┴─┴─┴─┘
    │     │                         
    │ 7   │◄── INPUT_PULLUP (Column 0)
    │ 8   │◄── INPUT_PULLUP (Column 1)
    │ 9   │◄── INPUT_PULLUP (Column 2)
    │ 10  │◄── INPUT_PULLUP (Column 3)
    │ 11  │◄── INPUT_PULLUP (Column 4)
    │ 12  │◄── INPUT_PULLUP (Column 5)
    │     │
    │ GND │────── COMMON GROUND
    └─────┘
```

### LED Indicators

```
Arduino          Resistor        LED
────────         ────────        ───
    ┌─────┐
    │ A1  │───[220Ω]───►├─(─)─┤───► GND   (Green)
    │ A2  │───[220Ω]───►├─(─)─┤───► GND   (Yellow)
    │ A3  │───[220Ω]───►├─(─)─┤───► GND   (Red)
    │ GND │─────────────────────┴─────────
    └─────┘
```

### Buzzer

```
Arduino          Buzzer
────────         ──────
    ┌─────┐
    │ A0  │───►(+) buzzer (-)───► GND
    └─────┘
```

### LCD Display

```
Arduino          I2C LCD Module
────────         ───────────────
    ┌─────┐
    │ A4  │───► SDA
    │ A5  │───► SCL
    │ 5V  │───► VCC
    │ GND │───► GND
    └─────┘
```

---

## Wiring Color Code

| Function | Recommended Color |
|----------|------------------|
| Row wires | Red |
| Column wires | Black |
| LED Green | Green |
| LED Yellow | Yellow |
| LED Red | Red |
| Buzzer | Orange |
| LCD SDA | Blue |
| LCD SCL | Purple |
| Power (5V) | Red |
| Ground | Black |

---

## Assembly Tips

1. **Use Color-Coded Wires**: Makes debugging easier
2. **Organize with Cable Ties**: Keep wires neat
3. **Label Everything**: Mark each wire group
4. **Test Row by Row**: Test each row of buttons during assembly
5. **Check Polarity**: LEDs and buzzer are polarity-sensitive
6. **Secure Components**: Use tape or glue to secure LCD

---

## Breadboard Layout Example

```
    ┌──────────────────────────────────────────────────────────┐
    │  Arduino Uno                                              │
    │  ┌────┐                                                  │
    │  │USB │                                                  │
    │  └──┬─┘                                                  │
    │    │                                                     │
    │  ┌─┴────────────────────────────────────────────┐        │
    │  │                                                    │        │
    │  │  5V ──── LCD VCC (Red)                         │        │
    │  │  GND ─── LCD GND, Button Ground (Black)         │        │
    │  │  A0 ──── Buzzer (Orange)                        │        │
    │  │  A1 ──── LED Green (Green)                      │        │
    │  │  A2 ──── LED Yellow (Yellow)                    │        │
    │  │  A3 ──── LED Red (Red)                          │        │
    │  │  A4 ──── LCD SDA (Blue)                         │        │
    │  │  A5 ──── LCD SCL (Purple)                       │        │
    │  │  2-6 ─── Button Rows (Red)                      │        │
    │  │  7-12 ── Button Columns (Black)                  │        │
    │  │                                                    │        │
    │  └──────────────────────────────────────────────────┘        │
    │                                                             │
    │  ┌──────────────────────────────────────────────────┐        │
    │  │              Breadboard                          │        │
    │  │                                                │        │
    │  │  [5x6 Button Matrix]                           │        │
    │  │                                                │        │
    │  │  [LCD Display Module]                          │        │
    │  │                                                │        │
    │  │  [LEDs + Resistors]                           │        │
    │  │                                                │        │
    │  │  [Buzzer]                                     │        │
    │  └──────────────────────────────────────────────────┘        │
    └──────────────────────────────────────────────────────────────┘
```

---

## Final Checklist

- [ ] All row pins (2-6) connected to button rows
- [ ] All column pins (7-12) connected to button columns
- [ ] Internal pullups enabled for column pins
- [ ] 220Ω resistors in series with each LED
- [ ] LEDs connected with correct polarity
- [ ] Buzzer connected with correct polarity
- [ ] LCD I2C address confirmed (default 0x27)
- [ ] LCD SDA/SCL connected correctly
- [ ] All GND connections common
- [ ] No loose wires or shorts
- [ ] Power supply verified (USB 5V)
