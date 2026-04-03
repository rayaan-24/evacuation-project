# STEP-BY-STEP WIRING VISUAL GUIDE
## For AI Image Generation Prompts

Use these 10 prompts to generate circuit diagrams. Follow them in order (Step 1 → Step 10).

---

## GENERATION PROMPT 1: ESP32 PINS

```
Create a clear, labeled circuit diagram showing the ESP32 DevKit v1 pin layout from a top-down view. 
Include and LABEL these elements:
- Power pins: 3.3V (2 locations), 5V, GND (multiple)
- GPIO pins in a row: GPIO4, GPIO5, GPIO6, GPIO7, GPIO8, GPIO9, GPIO10, GPIO11, GPIO12, GPIO13, GPIO14, GPIO15, GPIO16, GPIO17
- Additional pins: EN (Enable), TX, RX
- USB connector at bottom (show as rectangle)
- Board outline: rectangular shape approximately 5cm x 3cm

Style: Clean technical diagram with white background, black labels, color-coded pins. 
Use blue for power pins, green for GPIO, orange for data pins, black for GND.
Make labels large and readable. Professional engineering style.
```

---

## GENERATION PROMPT 2: BREADBOARD

```
Create a circuit diagram showing a half-size (400-point) breadboard from a top-down view.
Include and LABEL:
- Center groove running horizontally (divide top and bottom sections)
- Positive (+) rail at top (colored red)
- Negative (-) rail at top (colored blue)
- Positive (+) rail at bottom (colored red)
- Negative (-) rail at bottom (colored blue)
- Numbered rows on left side: 1, 5, 10, 15, 20, 25, 30
- Lettered columns: A, B, C, D, E (top), F, G, H, I, J (bottom)

Style: Clean white background, colored rails, clear numbering. 
Show all 30 holes per side clearly. Professional look.
Dimensions shown: approximately 8cm x 5cm.
```

---

## GENERATION PROMPT 3: BUTTON IDENTIFICATION

```
Create an educational circuit diagram showing a tactile push button's internal structure.
Show THREE views of the button:
1. TOP VIEW: Square button from above, 4 legs visible, labeled leg 1, 2, 3, 4
2. SIDE VIEW: Show button shape, indicate which legs connect internally
3. CIRCUIT SYMBOL: Standard push button switch symbol

Include annotations showing:
- "Leg 1 connects to Leg 2 internally" 
- "Leg 3 connects to Leg 4 internally"
- "When pressed, ALL legs connect together"
- "Legs 1-2 and legs 3-4 are separate pairs"

Style: Educational diagram with white background, blue for button, yellow highlights for connections.
Use arrows to show current flow when pressed.
Include dimensions: 6mm x 6mm x 5mm height.
```

---

## GENERATION PROMPT 4: ROW WIRING (GPIO 4-8)

```
Create a circuit diagram showing how to wire 5 rows of buttons to ESP32 GPIO pins.

LEFT SIDE:
- ESP32 DevKit (simplified rectangle with labeled pins)

RIGHT SIDE:
- 30 buttons arranged in 5 rows, 6 columns
- Each row labeled: Row 0, Row 1, Row 2, Row 3, Row 4

WIRING TO SHOW:
- GPIO4 → All buttons in Row 0 (orange wire)
- GPIO5 → All buttons in Row 1 (orange wire)
- GPIO6 → All buttons in Row 2 (orange wire)
- GPIO7 → All buttons in Row 3 (orange wire)
- GPIO8 → All buttons in Row 4 (orange wire)

Style: Clean diagram, white background, orange wires for row connections.
Use distinct wire paths, not overlapping. Include pin numbers near connections.
Show junction dots where multiple wires connect.
```

---

## GENERATION PROMPT 5: COLUMN WIRING (GPIO 9-14)

```
Create a circuit diagram showing how to wire 6 columns of buttons to ESP32 GPIO pins.

LEFT SIDE:
- ESP32 DevKit (simplified rectangle with labeled pins)

RIGHT SIDE:
- 30 buttons arranged in 5 rows, 6 columns
- Each column labeled: Col0, Col1, Col2, Col3, Col4, Col5

WIRING TO SHOW:
- GPIO9 → All buttons in Column 0: buttons 0, 6, 12, 18, 24 (blue wire)
- GPIO10 → All buttons in Column 1: buttons 1, 7, 13, 19, 25 (blue wire)
- GPIO11 → All buttons in Column 2: buttons 2, 8, 14, 20, 26 (blue wire)
- GPIO12 → All buttons in Column 3: buttons 3, 9, 15, 21, 27 (blue wire)
- GPIO13 → All buttons in Column 4: buttons 4, 10, 16, 22, 28 (blue wire)
- GPIO14 → All buttons in Column 5: buttons 5, 11, 17, 23, 29 (blue wire)

Style: Clean diagram, white background, blue wires for column connections.
Use distinct wire paths, clearly showing column grouping.
Include button numbers at each connection point.
```

---

## GENERATION PROMPT 6: GROUND WIRING

```
Create a circuit diagram showing the common ground connection for the button matrix.

CENTER:
- ESP32 DevKit showing GND pins highlighted in black
- Breadboard with 30 buttons in 5x6 grid

WIRING TO SHOW:
- ESP32 GND pin → Breadboard negative rail (black wire)
- Negative rail → Leg 3 of ALL 30 buttons (black wires)
- Negative rail → Leg 4 of ALL 30 buttons (black wires)

Style: Clean diagram, white background, BLACK wires for all ground connections.
Use thick black lines for GND rail.
Show GND symbol (downward pointing triangle with horizontal line).
Include text label: "ALL BUTTONS SHARE COMMON GROUND"
Make it clear this is the return path for all button circuits.
```

---

## GENERATION PROMPT 7: COMPLETE BUTTON MATRIX

```
Create a comprehensive circuit diagram showing the COMPLETE 30-button matrix wiring.

LEFT SIDE:
- ESP32 DevKit v1 with ALL GPIO pins labeled
- Pin colors: Orange for rows (4-8), Blue for columns (9-14), Black for GND

CENTER:
- Half-size breadboard with labeled rails
- 30 buttons in perfect 5×6 grid
- Button numbers shown: 0-29

WIRING SHOWN:
- Row connections: GPIO4-8 (ORANGE)
- Column connections: GPIO9-14 (BLUE)  
- Ground connections: GND (BLACK)

ADDITIONAL INFO:
- Table showing Button = Row×6 + Column
- Color legend in corner
- Connection summary box

Style: Professional engineering diagram, white background, clean organization.
This should be a complete reference showing ALL connections at once.
Include a zoomed detail view of one button showing all 4 legs and their connections.
```

---

## GENERATION PROMPT 8: LED WIRING

```
Create a circuit diagram showing the 3 status LED wiring.

LEFT SIDE:
- ESP32 showing GPIO15, GPIO16, GPIO17 highlighted

RIGHT SIDE:
- 3 LEDs arranged horizontally: RED, YELLOW, GREEN
- 3 resistors (220Ω) positioned before each LED

CIRCUIT FOR EACH LED:
GPIO15 → 220Ω Resistor → RED LED Anode (+) → RED LED Cathode (-) → GND
GPIO16 → 220Ω Resistor → YELLOW LED Anode (+) → YELLOW LED Cathode (-) → GND
GPIO17 → 220Ω Resistor → GREEN LED Anode (+) → GREEN LED Cathode (-) → GND

STYLE:
- Use RED wire for GPIO15 connection
- Use YELLOW wire for GPIO16 connection  
- Use GREEN wire for GPIO17 connection
- Use BLACK wires for GND connections
- Clearly show resistor placement (before LED)
- Show LED polarity: long leg = anode (+), short leg = cathode (-)
- Include resistor color bands: Brown-Red-Brown (220Ω)

Include a detail box showing LED polarity identification.
```

---

## GENERATIVE PROMPT 9: COMPLETE SYSTEM OVERVIEW

```
Create a professional poster-style circuit diagram showing the COMPLETE ESP32 Emergency Controller system.

TOP SECTION:
- Title: "ESP32 Emergency Controller - Complete Wiring Diagram"
- ESP32 DevKit centered with all GPIO pins labeled and color-coded

MIDDLE SECTION:
- 30-button matrix (5×6) on breadboard
- All row wires (orange)
- All column wires (blue)
- All ground wires (black)

BOTTOM SECTION:
- 3 status LEDs with resistors
- GPIO15 → Red LED
- GPIO16 → Yellow LED  
- GPIO17 → Green LED

SIDEBAR:
- Component list with quantities
- Pin assignment table
- Wire color legend
- Assembly notes

STYLE:
- Professional engineering diagram
- Color-coded wires for easy identification
- Clear section divisions
- Large, readable labels
- Suitable for printing on A3 paper
- White background with minimal decorations
```

---

## GENERATION PROMPT 10: PHYSICAL LAYOUT (3D)

```
Create a 3D-style visualization showing how all components are physically arranged on the breadboard.

VIEW: Isometric 3D perspective from above-front

SHOW:
- ESP32 DevKit at top, USB connector facing up
- Breadboard below ESP32
- 30 buttons in 5×6 grid on breadboard center
- 3 LEDs at bottom of breadboard
- Jumper wires shown as actual rounded wires
- Resistors shown as small cylindrical components
- Breadboard color: beige/cream
- ESP32 color: blue-green
- Button color: black with gray top

INCLUDE:
- Size comparison: breadboard should be full width
- Clear spatial relationships
- Labels for major components
- Wire routing visible (not hidden under components)

STYLE:
- Realistic 3D render appearance
- Soft lighting, slight shadows
- Clean, modern technical illustration style
- White or light gray background
- Components should look tangible and real
```

---

## USAGE INSTRUCTIONS

### For ChatGPT/DALL-E:
1. Copy ONE prompt at a time
2. Paste into the chat
3. Wait for image generation
4. Save the image with appropriate name
5. Proceed to next prompt

### Image Naming Convention:
```
01_esp32_pins.png
02_breadboard.png
03_button_identification.png
04_row_wiring.png
05_column_wiring.png
06_ground_wiring.png
07_complete_matrix.png
08_led_wiring.png
09_system_overview.png
10_physical_layout.png
```

### Recommended Tools:
| Tool | Link | Best For |
|------|------|----------|
| ChatGPT (with DALL-E 3) | chat.openai.com | High quality, detailed |
| Microsoft Copilot | copilot.microsoft.com | Free, Bing integration |
| Leonardo AI | leonardo.ai | Technical diagrams |
| Bing Image Creator | bing.com/create | Free, DALL-E 3 |

### Tips for Best Results:
- Use ChatGPT Plus or Copilot for highest quality
- Add " photorealistic" or " detailed" if needed
- For circuits, specify " technical diagram" or " engineering drawing"
- If first result is poor, regenerate with slight prompt modification
- Save multiple versions and compare

---

## COMPLETE PROJECT CHECKLIST

After generating all 10 diagrams:

- [ ] Step 1: ESP32 Pins diagram
- [ ] Step 2: Breadboard diagram
- [ ] Step 3: Button identification diagram
- [ ] Step 4: Row wiring diagram
- [ ] Step 5: Column wiring diagram
- [ ] Step 6: Ground wiring diagram
- [ ] Step 7: Complete button matrix diagram
- [ ] Step 8: LED wiring diagram
- [ ] Step 9: System overview diagram
- [ ] Step 10: Physical layout diagram

Print all diagrams and follow them in order while building!

---

**Follow the main guide (COMPLETE_BUILD_GUIDE.md) for detailed step-by-step instructions!**
