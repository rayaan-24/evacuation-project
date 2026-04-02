/*
  ESP32 Configuration - WiFi Settings
  ===================================
  
  SETUP INSTRUCTIONS:
  
  1. Open this file in Arduino IDE
  2. Edit the WiFi credentials below
  3. Edit the API_HOST to match your PC's IP
  4. Upload to ESP32
  
  FINDING YOUR PC IP:
  
  Windows:
  - Open Command Prompt
  - Type: ipconfig
  - Look for "IPv4 Address" (e.g., 192.168.1.100)
  
  Mac/Linux:
  - Open Terminal
  - Type: ifconfig
  - Look for "inet" under WiFi (e.g., 192.168.1.100)
  
  WIRING DIAGRAM:
  
  ESP32 GPIO 4  ──→ Row 0 buttons (0, 1, 2, 3, 4, 5)
  ESP32 GPIO 5  ──→ Row 1 buttons (6, 7, 8, 9, 10, 11)
  ESP32 GPIO 6  ──→ Row 2 buttons (12, 13, 14, 15, 16, 17)
  ESP32 GPIO 7  ──→ Row 3 buttons (18, 19, 20, 21, 22, 23)
  ESP32 GPIO 8  ──→ Row 4 buttons (24, 25, 26, 27, 28, 29)
  
  ESP32 GPIO 9  ──→ Column 0 (buttons 0, 6, 12, 18, 24)
  ESP32 GPIO 10 ──→ Column 1 (buttons 1, 7, 13, 19, 25)
  ESP32 GPIO 11 ──→ Column 2 (buttons 2, 8, 14, 20, 26)
  ESP32 GPIO 12 ──→ Column 3 (buttons 3, 9, 15, 21, 27)
  ESP32 GPIO 13 ──→ Column 4 (buttons 4, 10, 16, 22, 28)
  ESP32 GPIO 14 ──→ Column 5 (buttons 5, 11, 17, 23, 29)
  
  ESP32 GND ─────────→ All buttons (common ground)
  
  Status LEDs:
  ESP32 GPIO 2  ──→ Built-in LED (WiFi status)
  ESP32 GPIO 15 ──→ 220Ω ─→ Red LED (+) ──→ GND
  ESP32 GPIO 16 ──→ 220Ω ─→ Yellow LED (+) ──→ GND
  ESP32 GPIO 17 ──→ 220Ω ─→ Green LED (+) ──→ GND
  ESP32 GPIO 18 ──→ Buzzer (+) ──→ GND
*/

#ifndef CONFIG_H
#define CONFIG_H

// ========================================
// WIFI CREDENTIALS - EDIT THESE!
// ========================================

// Your WiFi Network Name (SSID)
#define WIFI_SSID "YourWiFiName"

// Your WiFi Password
#define WIFI_PASSWORD "YourWiFiPassword"

// ========================================
// API SERVER - EDIT THIS!
// ========================================

// Your PC's IP address on the network
// Examples:
//   - "http://192.168.1.100:5000"
//   - "http://192.168.0.50:5000"
// #define API_HOST "http://192.168.1.100:5000"
#define API_HOST "https://evacuation-project.onrender.com/"

// ========================================
// DEVICE IDENTIFICATION
// ========================================

// Unique ID for this ESP32 (for multi-device setups)
#define DEVICE_ID "ESP32-001"

// Physical location description
#define DEVICE_LOCATION "Smart Evacuation Floor 1"

#endif // CONFIG_H
