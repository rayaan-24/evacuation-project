/*
  ESP32 Configuration File
  ========================
  For ESP32 DevKit V1 (DOIT)
  Micro-USB on top, BOOT button on left, EN button on right
  
  SETUP INSTRUCTIONS:
  
  1. Open this file in Arduino IDE
  2. Edit the WiFi credentials below
  3. Edit the API_HOST to match your PC's IP
  4. Upload to ESP32
  
  FINDING YOUR PC IP:
  
  Windows:
  - Open Command Prompt (Win+R, type "cmd", Enter)
  - Type: ipconfig
  - Look for "IPv4 Address" (e.g., 192.168.1.100)
  
  Mac/Linux:
  - Open Terminal
  - Type: ifconfig
  - Look for "inet" under WiFi
  
  PIN LAYOUT FOR ESP32 DevKit V1 (DOIT):
  ═══════════════════════════════════════════════════════════════════════════════
  
  LEFT SIDE (top to bottom): 3V3, GND, D15, D2, D4, RX2, TX2, D5, D18, D19, 
                              D21, RX0, TX0, D22, D23
  
  RIGHT SIDE (top to bottom): VIN, GND, D13, D12, D14, D27, D26, D25, D33, 
                               D32, D35, D34, VN, VP, EN
  
  WHERE Dxx = GPIO xx
  
  WIRING DIAGRAM (5x6 Matrix = 30 buttons):
  ═══════════════════════════════════════════════════════════════════════════════
  
  ROW PINS (OUTPUT - Drive LOW when scanning):
  ─────────────────────────────────────────────────────────────────────────────
  D4  (GPIO 4)  ──→ Row 0 buttons (0, 1, 2, 3, 4, 5)
  D5  (GPIO 5)  ──→ Row 1 buttons (6, 7, 8, 9, 10, 11)
  D14 (GPIO 14) ──→ Row 2 buttons (12, 13, 14, 15, 16, 17)
  D18 (GPIO 18) ──→ Row 3 buttons (18, 19, 20, 21, 22, 23)
  D19 (GPIO 19) ──→ Row 4 buttons (24, 25, 26, 27, 28, 29)
  
  COLUMN PINS (INPUT_PULLUP - Detect button press):
  ─────────────────────────────────────────────────────────────────────────────
  D13 (GPIO 13) ──→ Column 0 (buttons 0, 6, 12, 18, 24)
  D21 (GPIO 21) ──→ Column 1 (buttons 1, 7, 13, 19, 25)
  D22 (GPIO 22) ──→ Column 2 (buttons 2, 8, 14, 20, 26)
  D23 (GPIO 23) ──→ Column 3 (buttons 3, 9, 15, 21, 27)
  D25 (GPIO 25) ──→ Column 4 (buttons 4, 10, 16, 22, 28)
  D26 (GPIO 26) ──→ Column 5 (buttons 5, 11, 17, 23, 29)
  
  STATUS INDICATORS:
  ─────────────────────────────────────────────────────────────────────────────
  D2  (GPIO 2)  ──→ Built-in LED (WiFi status) [ALREADY ON BOARD]
  D15 (GPIO 15) ──→ 220Ω resistor → Red LED (+) → GND
  D27 (GPIO 27) ──→ Buzzer (+) → GND
  
  POWER:
  ─────────────────────────────────────────────────────────────────────────────
  3V3  ──────────→ (+) Positive rail (3.3V)
  GND  ──────────→ (-) Negative rail (GND)
  
  PULL-UP RESISTORS (10kΩ each):
  ─────────────────────────────────────────────────────────────────────────────
  Each column pin needs a 10kΩ resistor to 3.3V rail
  This keeps the pin HIGH when button is not pressed
  
  GPIO PINS TO AVOID:
  ─────────────────────────────────────────────────────────────────────────────
  • D6, D7, D8, D9, D10, D11 (GPIO 6-11) ─→ Flash memory, DO NOT USE
  • D12 (GPIO 12) ─→ Boot strap pin, use with caution
  • D2 (GPIO 2) ─→ Boot strap pin, use with caution (but OK for LED)
  • D0 (GPIO 0) ─→ Boot pin, affects boot mode
  • D35, D34, VN, VP (GPIO 34-39) ─→ Input only, no output
*/

#ifndef CONFIG_H
#define CONFIG_H

// ========================================
// WIFI CREDENTIALS - EDIT THESE!
// ========================================

// Your WiFi Network Name (SSID)
// Must be 2.4GHz (ESP32 doesn't support 5GHz WiFi)
#define WIFI_SSID "YOUR_WIFI_SSID"

// Your WiFi Password
#define WIFI_PASSWORD "YOUR_WIFI_PASSWORD"

// ========================================
// API SERVER - EDIT THIS!
// ========================================

// Your computer's IP address on the network
// Examples:
//   - Local network: "http://192.168.1.100:5000"
//   - Cloud (Render): "https://your-app.onrender.com/"

#define API_HOST "http://YOUR_PC_IP:5000"

// ========================================
// DEVICE IDENTIFICATION
// ========================================

// Unique ID for this ESP32 (change if using multiple ESP32s)
#define DEVICE_ID "ESP32-001"

// Physical location description
#define DEVICE_LOCATION "Smart Evacuation Floor 1"

#endif // CONFIG_H
