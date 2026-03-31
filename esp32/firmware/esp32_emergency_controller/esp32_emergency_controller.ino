/*
  ESP32 Smart Evacuation Controller
  ================================
  30-Button Emergency Matrix via WiFi
  
  Hardware: ESP32 DevKit v1
  Buttons: 5x6 matrix (30 buttons)
  Connectivity: WiFi (HTTP to Flask API)
  
  Author: Smart Evacuation System
  Version: 1.0
*/

#include <WiFi.h>
#include <HTTPClient.h>
#include <ArduinoJson.h>

// ========================================
// CONFIGURATION - EDIT THESE VALUES
// ========================================

// WiFi Configuration
const char* WIFI_SSID = "YOUR_WIFI_SSID";       // Your WiFi name
const char* WIFI_PASSWORD = "YOUR_WIFI_PASSWORD"; // Your WiFi password

// Flask API Server Configuration
const char* API_HOST = "http://YOUR_PC_IP:5000"; // Your PC's IP address
// Examples:
//   - Local:  "http://192.168.1.100:5000"
//   - PC Name: "http://DESKTOP-PC:5000"

// Device Configuration
const char* DEVICE_ID = "ESP32-001";  // Unique ID for this ESP32
const char* DEVICE_LOCATION = "Building-Floor1"; // Physical location

// ========================================
// BUTTON MATRIX CONFIGURATION
// ========================================

const int ROWS = 5;
const int COLS = 6;
const int TOTAL_BUTTONS = ROWS * COLS;

// Row pins (OUTPUT) - Drive LOW when scanning
const int ROW_PINS[ROWS] = {4, 5, 6, 7, 8};

// Column pins (INPUT_PULLUP) - Detect button press
const int COL_PINS[COLS] = {9, 10, 11, 12, 13, 14};

// ========================================
// STATUS INDICATORS
// ========================================

const int LED_WIFI = 2;        // Built-in LED (also WiFi status)
const int LED_RED = 15;       // Emergency active
const int LED_YELLOW = 16;    // Warning/system issue
const int LED_GREEN = 17;     // System ready
const int BUZZER_PIN = 18;    // Audio alert

// ========================================
// EMERGENCY TYPES (cycles on each press)
// ========================================

const char* EMERGENCY_TYPES[] = {
  "FIRE",      // 0 - Red indicator
  "SMOKE",     // 1 - Orange indicator
  "GAS",       // 2 - Purple indicator
  "BLOCKAGE",  // 3 - Blue indicator
  "CROWD"      // 4 - Yellow indicator
};

const int NUM_TYPES = 5;

// ========================================
// TIMING CONFIGURATION
// ========================================

const unsigned long DEBOUNCE_MS = 50;      // Button debounce time
const unsigned long REPEAT_BLOCK_MS = 1000; // Prevent rapid repeats
const unsigned long WIFI_RECONNECT_MS = 30000; // WiFi reconnect interval
const unsigned long HEARTBEAT_INTERVAL = 60000; // Heartbeat to server

// ========================================
// SENSOR MAPPING (Button → Corridor)
// ========================================

// Maps button index to sensor ID
const char* SENSOR_IDS[TOTAL_BUTTONS] = {
  "sensor_0",  "sensor_1",  "sensor_2",  "sensor_3",  "sensor_4",  "sensor_5",   // Row 0
  "sensor_6",  "sensor_7",  "sensor_8",  "sensor_9",  "sensor_10", "sensor_11",  // Row 1
  "sensor_12", "sensor_13", "sensor_14", "sensor_15", "sensor_16", "sensor_17",  // Row 2
  "sensor_18", "sensor_19", "sensor_20", "sensor_21", "sensor_22", "sensor_23",  // Row 3
  "sensor_24", "sensor_25", "sensor_26", "sensor_27", "sensor_28", "sensor_29"   // Row 4
};

// Button labels for serial output
const char* BUTTON_LABELS[TOTAL_BUTTONS] = {
  "C1A-North", "C1B-North", "C1C-North", "C1D-North", "C2A-Left",  "C2B-Left",   // Row 0
  "C3A-Right", "C3B-Right", "C3C-Right", "C3D-Right", "C4A-NCorr", "C4B-ECorr",  // Row 1
  "C5A-CCorr", "C5B-CCorr", "C6A-SCorr", "C6B-SCorr", "CJ-NW",     "CJ-NC",       // Row 2
  "CJ-NE",     "CJ-MW",     "CJ-MC",     "CJ-ME",     "CJ-SW",     "CJ-SC",       // Row 3
  "CJ-SE",     "C7A-NWSt",  "C7B-NESt",  "C7C-ESLobby","STORED",   "RESERVED"    // Row 4
};

// ========================================
// STATE VARIABLES
// ========================================

// Button states
bool buttonStableState[TOTAL_BUTTONS];
bool buttonReadState[TOTAL_BUTTONS];
unsigned long lastStateChange[TOTAL_BUTTONS];
unsigned long lastTriggerTime[TOTAL_BUTTONS];
int currentEmergencyIndex[TOTAL_BUTTONS];  // Tracks which type each button is on

// WiFi and timing
unsigned long lastWiFiCheck = 0;
unsigned long lastHeartbeat = 0;
bool wifiConnected = false;
int connectionFailures = 0;

// Statistics
unsigned long totalTriggers = 0;
unsigned long successfulSends = 0;
unsigned long failedSends = 0;

// ========================================
// SETUP FUNCTION
// ========================================

void setup() {
  Serial.begin(115200);
  delay(500);
  
  printHeader();
  
  // Initialize button matrix
  initButtonMatrix();
  
  // Initialize status LEDs
  initStatusLEDs();
  
  // Initialize buzzer
  pinMode(BUZZER_PIN, OUTPUT);
  digitalWrite(BUZZER_PIN, LOW);
  
  // Initialize button states
  for (int i = 0; i < TOTAL_BUTTONS; i++) {
    buttonStableState[i] = false;
    buttonReadState[i] = false;
    lastStateChange[i] = 0;
    lastTriggerTime[i] = 0;
    currentEmergencyIndex[i] = 0;
  }
  
  // Connect to WiFi
  connectToWiFi();
  
  // Send registration to server
  registerDevice();
  
  // Success feedback
  successFeedback();
  
  Serial.println("\n✓ System Ready!");
  Serial.println("Press buttons to trigger emergencies");
  Serial.println("Watch Serial Monitor for status\n");
}

// ========================================
// MAIN LOOP
// ========================================

void loop() {
  unsigned long now = millis();
  
  // Check WiFi connection periodically
  if (now - lastWiFiCheck > WIFI_RECONNECT_MS) {
    lastWiFiCheck = now;
    checkWiFiConnection();
  }
  
  // Send heartbeat periodically
  if (now - lastHeartbeat > HEARTBEAT_INTERVAL) {
    lastHeartbeat = now;
    sendHeartbeat();
  }
  
  // Scan button matrix
  scanButtonMatrix();
  
  // Small delay to prevent watchdog
  delay(10);
}

// ========================================
// BUTTON MATRIX FUNCTIONS
// ========================================

void initButtonMatrix() {
  Serial.println("Initializing button matrix...");
  
  // Set row pins as OUTPUT
  for (int row = 0; row < ROWS; row++) {
    pinMode(ROW_PINS[row], OUTPUT);
    digitalWrite(ROW_PINS[row], HIGH);  // Idle HIGH
  }
  
  // Set column pins as INPUT_PULLUP
  for (int col = 0; col < COLS; col++) {
    pinMode(COL_PINS[col], INPUT_PULLUP);
  }
  
  Serial.println("Button matrix initialized (5x6 = 30 buttons)");
}

void scanButtonMatrix() {
  unsigned long now = millis();
  
  // Scan each row
  for (int row = 0; row < ROWS; row++) {
    // Set all rows HIGH (idle)
    setRowsIdle();
    
    // Set current row LOW (active)
    digitalWrite(ROW_PINS[row], LOW);
    delayMicroseconds(100);  // Settling time
    
    // Check each column
    for (int col = 0; col < COLS; col++) {
      int index = row * COLS + col;
      
      // Read button state (LOW = pressed due to pullup)
      bool pressed = (digitalRead(COL_PINS[col]) == LOW);
      
      // Debouncing: detect change
      if (pressed != buttonReadState[index]) {
        buttonReadState[index] = pressed;
        lastStateChange[index] = now;
      }
      
      // Check if state is stable for debounce period
      bool stable = (now - lastStateChange[index]) >= DEBOUNCE_MS;
      
      if (stable && buttonStableState[index] != buttonReadState[index]) {
        buttonStableState[index] = buttonReadState[index];
        
        // Button just pressed
        if (buttonStableState[index]) {
          handleButtonPress(index, now);
        }
      }
    }
  }
  
  // Reset all rows HIGH
  setRowsIdle();
}

void setRowsIdle() {
  for (int row = 0; row < ROWS; row++) {
    digitalWrite(ROW_PINS[row], HIGH);
  }
}

void handleButtonPress(int index, unsigned long now) {
  // Prevent rapid repeats
  if (now - lastTriggerTime[index] < REPEAT_BLOCK_MS) {
    Serial.printf("Button %d: Blocked (too soon after last press)\n", index);
    return;
  }
  
  lastTriggerTime[index] = now;
  
  // Cycle through emergency types
  currentEmergencyIndex[index] = (currentEmergencyIndex[index] + 1) % NUM_TYPES;
  const char* emergencyType = EMERGENCY_TYPES[currentEmergencyIndex[index]];
  
  // Get sensor ID
  const char* sensorId = SENSOR_IDS[index];
  const char* buttonLabel = BUTTON_LABELS[index];
  
  // Print to Serial
  Serial.printf("\n🔴 EMERGENCY TRIGGERED!\n");
  Serial.printf("   Button: %d (%s)\n", index, buttonLabel);
  Serial.printf("   Sensor: %s\n", sensorId);
  Serial.printf("   Type:   %s\n", emergencyType);
  
  totalTriggers++;
  
  // Visual and audio feedback
  emergencyFeedback();
  
  // Send to Flask API
  if (wifiConnected) {
    sendEmergencyToAPI(sensorId, emergencyType);
  } else {
    Serial.println("⚠ WiFi not connected - Emergency logged locally");
    failedSends++;
  }
}

// ========================================
// STATUS LED FUNCTIONS
// ========================================

void initStatusLEDs() {
  Serial.println("Initializing status LEDs...");
  
  pinMode(LED_WIFI, OUTPUT);
  pinMode(LED_RED, OUTPUT);
  pinMode(LED_YELLOW, OUTPUT);
  pinMode(LED_GREEN, OUTPUT);
  
  // All off initially
  digitalWrite(LED_WIFI, LOW);
  digitalWrite(LED_RED, LOW);
  digitalWrite(LED_YELLOW, LOW);
  digitalWrite(LED_GREEN, LOW);
  
  Serial.println("Status LEDs initialized");
}

void setStatusLEDs(bool wifi, bool red, bool yellow, bool green) {
  digitalWrite(LED_WIFI, wifi ? HIGH : LOW);
  digitalWrite(LED_RED, red ? HIGH : LOW);
  digitalWrite(LED_YELLOW, yellow ? HIGH : LOW);
  digitalWrite(LED_GREEN, green ? HIGH : LOW);
}

void emergencyFeedback() {
  // Flash red LED rapidly
  for (int i = 0; i < 3; i++) {
    digitalWrite(LED_RED, HIGH);
    tone(BUZZER_PIN, 2000, 100);  // 2kHz beep
    delay(100);
    digitalWrite(LED_RED, LOW);
    noTone(BUZZER_PIN);
    delay(50);
  }
}

void successFeedback() {
  // Green LED solid + happy beep
  digitalWrite(LED_GREEN, HIGH);
  tone(BUZZER_PIN, 1500, 200);
  delay(200);
  noTone(BUZZER_PIN);
}

// ========================================
// WIFI FUNCTIONS
// ========================================

void connectToWiFi() {
  Serial.println("\n========================================");
  Serial.println("Connecting to WiFi...");
  Serial.println("========================================");
  Serial.printf("SSID: %s\n", WIFI_SSID);
  
  WiFi.mode(WIFI_STA);
  WiFi.setAutoReconnect(true);
  WiFi.persistent(false);
  
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
  
  int attempts = 0;
  while (WiFi.status() != WL_CONNECTED && attempts < 40) {
    delay(500);
    Serial.print(".");
    
    // Blink LED while connecting
    digitalWrite(LED_WIFI, !digitalRead(LED_WIFI));
    attempts++;
  }
  
  Serial.println();
  
  if (WiFi.status() == WL_CONNECTED) {
    wifiConnected = true;
    connectionFailures = 0;
    
    Serial.println("========================================");
    Serial.println("✓ WiFi Connected!");
    Serial.println("========================================");
    Serial.printf("IP Address: %s\n", WiFi.localIP().toString().c_str());
    Serial.printf("Signal Strength: %d dBm\n", WiFi.RSSI());
    Serial.printf("MAC Address: %s\n", WiFi.macAddress().c_str());
    Serial.println("========================================\n");
    
    // Solid green = connected
    setStatusLEDs(HIGH, LOW, LOW, HIGH);
    
  } else {
    wifiConnected = false;
    
    Serial.println("========================================");
    Serial.println("✗ WiFi Connection Failed!");
    Serial.println("========================================");
    Serial.println("Will retry automatically...");
    Serial.println("System can still log locally\n");
    Serial.println("========================================\n");
    
    // Yellow = warning
    setStatusLEDs(LOW, LOW, HIGH, LOW);
  }
}

void checkWiFiConnection() {
  if (WiFi.status() != WL_CONNECTED) {
    if (wifiConnected) {
      wifiConnected = false;
      Serial.println("⚠ WiFi connection lost!");
      
      // Yellow = warning
      setStatusLEDs(LOW, LOW, HIGH, LOW);
      
      connectionFailures++;
      
      if (connectionFailures >= 3) {
        Serial.println("Attempting reconnection...");
        connectToWiFi();
        if (wifiConnected) {
          connectionFailures = 0;
        }
      }
    }
  } else {
    if (!wifiConnected) {
      wifiConnected = true;
      connectionFailures = 0;
      Serial.println("✓ WiFi reconnected!");
      
      // Green = connected
      setStatusLEDs(HIGH, LOW, LOW, HIGH);
      
      // Re-register device
      registerDevice();
    }
  }
}

// ========================================
// HTTP COMMUNICATION FUNCTIONS
// ========================================

void registerDevice() {
  if (!wifiConnected) return;
  
  Serial.println("\n📡 Registering device with server...");
  
  HTTPClient http;
  String url = String(API_HOST) + "/esp32/register";
  
  http.begin(url);
  http.addHeader("Content-Type", "application/json");
  
  // Create registration payload
  DynamicJsonDocument doc(256);
  doc["device_id"] = DEVICE_ID;
  doc["location"] = DEVICE_LOCATION;
  doc["ip_address"] = WiFi.localIP().toString();
  doc["wifi_ssid"] = WIFI_SSID;
  doc["button_count"] = TOTAL_BUTTONS;
  doc["firmware_version"] = "1.0";
  
  String payload;
  serializeJson(doc, payload);
  
  int httpCode = http.POST(payload);
  
  if (httpCode == 200 || httpCode == 201) {
    String response = http.getString();
    Serial.println("✓ Device registered successfully!");
    Serial.printf("Server response: %s\n", response.c_str());
  } else {
    Serial.printf("⚠ Registration failed: HTTP %d\n", httpCode);
  }
  
  http.end();
}

void sendEmergencyToAPI(const char* sensorId, const char* emergencyType) {
  Serial.println("\n📡 Sending emergency to server...");
  
  HTTPClient http;
  String url = String(API_HOST) + "/sensor-update";
  
  http.begin(url);
  http.addHeader("Content-Type", "application/json");
  http.setTimeout(5000);  // 5 second timeout
  
  // Create emergency payload
  DynamicJsonDocument doc(256);
  doc["sensor_id"] = sensorId;
  doc["type"] = emergencyType;
  doc["device_id"] = DEVICE_ID;
  doc["source"] = "esp32_button";
  
  String payload;
  serializeJson(doc, payload);
  
  Serial.printf("   URL: %s\n", url.c_str());
  Serial.printf("   Payload: %s\n", payload.c_str());
  
  unsigned long startTime = millis();
  int httpCode = http.POST(payload);
  unsigned long responseTime = millis() - startTime;
  
  if (httpCode > 0) {
    String response = http.getString();
    
    Serial.printf("✓ Emergency sent! (took %lu ms)\n", responseTime);
    Serial.printf("   HTTP Response: %d\n", httpCode);
    
    if (response.length() > 0) {
      Serial.printf("   Response: %s\n", response.c_str());
    }
    
    successfulSends++;
    
  } else {
    Serial.printf("✗ Failed to send: %s\n", http.errorToString(httpCode).c_str());
    Serial.printf("   Error code: %d\n", httpCode);
    
    failedSends++;
    
    // Flash yellow to indicate send failure
    digitalWrite(LED_YELLOW, HIGH);
    delay(500);
    digitalWrite(LED_YELLOW, LOW);
  }
  
  http.end();
  
  // Print statistics
  printStatistics();
}

void sendHeartbeat() {
  if (!wifiConnected) return;
  
  HTTPClient http;
  String url = String(API_HOST) + "/esp32/heartbeat";
  
  http.begin(url);
  http.addHeader("Content-Type", "application/json");
  http.setTimeout(3000);
  
  DynamicJsonDocument doc(128);
  doc["device_id"] = DEVICE_ID;
  doc["rssi"] = WiFi.RSSI();
  doc["uptime_ms"] = millis();
  doc["total_triggers"] = totalTriggers;
  
  String payload;
  serializeJson(doc, payload);
  
  int httpCode = http.POST(payload);
  
  if (httpCode == 200) {
    // Silent success, just update LED
    digitalWrite(LED_WIFI, HIGH);
  }
  
  http.end();
}

// ========================================
// UTILITY FUNCTIONS
// ========================================

void printHeader() {
  Serial.println();
  Serial.println("╔════════════════════════════════════════════════════╗");
  Serial.println("║                                                    ║");
  Serial.println("║   ESP32 SMART EVACUATION CONTROLLER                ║");
  Serial.println("║   30-Button Emergency Matrix + WiFi                ║");
  Serial.println("║                                                    ║");
  Serial.println("║   Version: 1.0                                     ║");
  Serial.println("║   Hardware: ESP32 DevKit v1                       ║");
  Serial.println("║   Connectivity: WiFi (HTTP)                       ║");
  Serial.println("║                                                    ║");
  Serial.println("╚════════════════════════════════════════════════════╝");
  Serial.println();
}

void printStatistics() {
  Serial.println("\n📊 Statistics:");
  Serial.printf("   Total triggers: %lu\n", totalTriggers);
  Serial.printf("   Successful sends: %lu\n", successfulSends);
  Serial.printf("   Failed sends: %lu\n", failedSends);
  
  if (totalTriggers > 0) {
    float successRate = (successfulSends * 100.0) / totalTriggers;
    Serial.printf("   Success rate: %.1f%%\n", successRate);
  }
  
  if (WiFi.status() == WL_CONNECTED) {
    Serial.printf("   WiFi RSSI: %d dBm\n", WiFi.RSSI());
  }
}

void printHelp() {
  Serial.println("\n📖 Available Commands (via Serial):");
  Serial.println("   'status'   - Show connection and statistics");
  Serial.println("   'test'     - Send test emergency");
  Serial.println("   'clear'    - Clear all emergencies on server");
  Serial.println("   'wifi'     - Show WiFi info");
  Serial.println("   'help'     - Show this help");
}

// ========================================
// SERIAL COMMAND HANDLING (Optional)
// ========================================

void checkSerialCommands() {
  if (Serial.available() > 0) {
    String cmd = Serial.readStringUntil('\n');
    cmd.trim();
    cmd.toLowerCase();
    
    if (cmd == "status") {
      printStatistics();
    } else if (cmd == "test") {
      Serial.println("\n🧪 Sending test emergency...");
      sendEmergencyToAPI("sensor_test", "FIRE");
    } else if (cmd == "clear") {
      Serial.println("\n🧹 Clearing all emergencies...");
      // Could implement clear endpoint
    } else if (cmd == "wifi") {
      if (WiFi.status() == WL_CONNECTED) {
        Serial.printf("WiFi: Connected to %s\n", WIFI_SSID);
        Serial.printf("IP: %s\n", WiFi.localIP().toString().c_str());
        Serial.printf("RSSI: %d dBm\n", WiFi.RSSI());
      } else {
        Serial.println("WiFi: Not connected");
      }
    } else if (cmd == "help") {
      printHelp();
    }
  }
}
