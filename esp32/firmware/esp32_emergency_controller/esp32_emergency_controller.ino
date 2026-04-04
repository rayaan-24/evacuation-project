/*
  ESP32 Smart Evacuation Controller
  ================================
  30-Button Emergency Matrix via WiFi
  
  Hardware: ESP32 DevKit V1 (DOIT)
           - Micro-USB on top
           - BOOT button on LEFT
           - EN button on RIGHT
  
  Pins Used:
           - LEFT side: D4, D5, D14, D18, D19 (ROWS)
           - RIGHT side: D13, D21, D22, D23, D25, D26 (COLUMNS)
           - LEFT side: D2 (built-in LED), D15 (red LED), D27 (buzzer)
  
  Connectivity: WiFi (HTTP to Flask API)
  
  Author: Smart Evacuation System
  Version: 2.1
*/

#include <WiFi.h>
#include <HTTPClient.h>
#include <ArduinoJson.h>

// ========================================
// INCLUDE CONFIGURATION
// ========================================
#include "config.h"

// ========================================
// BUTTON MATRIX CONFIGURATION
// ========================================
// 5 rows x 6 columns = 30 buttons

const int ROWS = 5;
const int COLS = 6;
const int TOTAL_BUTTONS = ROWS * COLS;

// ROW pins (OUTPUT) - Drive one row LOW at a time to scan
// Using LEFT side pins: D4, D5, D14, D18, D19
const int ROW_PINS[ROWS] = {
    4,    // ROW 0 → D4  → Buttons 0, 1, 2, 3, 4, 5
    5,    // ROW 1 → D5  → Buttons 6, 7, 8, 9, 10, 11
    14,   // ROW 2 → D14 → Buttons 12, 13, 14, 15, 16, 17
    18,   // ROW 3 → D18 → Buttons 18, 19, 20, 21, 22, 23
    19    // ROW 4 → D19 → Buttons 24, 25, 26, 27, 28, 29
};

// COLUMN pins (INPUT_PULLUP) - Detect button presses
// Using RIGHT side pins: D13, D21, D22, D23, D25, D26
const int COL_PINS[COLS] = {
    13,   // COL 0 → D13 → Buttons 0, 6, 12, 18, 24
    21,   // COL 1 → D21 → Buttons 1, 7, 13, 19, 25
    22,   // COL 2 → D22 → Buttons 2, 8, 14, 20, 26
    23,   // COL 3 → D23 → Buttons 3, 9, 15, 21, 27
    25,   // COL 4 → D25 → Buttons 4, 10, 16, 22, 28
    26    // COL 5 → D26 → Buttons 5, 11, 17, 23, 29
};

// ========================================
// STATUS INDICATORS
// ========================================
// Using LEFT side pins

const int LED_BUILTIN = 2;     // D2  → Built-in LED (WiFi status)
const int LED_RED = 15;        // D15 → Red LED (Emergency indicator)
const int BUZZER_PIN = 27;     // D27 → Buzzer (Audio alert)

// ========================================
// EMERGENCY TYPES
// ========================================
// Cycles through these types with each button press

const char* EMERGENCY_TYPES[] = {
    "FIRE",      // Type 0
    "SMOKE",     // Type 1
    "GAS",       // Type 2
    "BLOCKAGE",  // Type 3
    "CROWD"      // Type 4
};

const int NUM_EMERGENCY_TYPES = 5;

// ========================================
// TIMING CONFIGURATION
// ========================================

const unsigned long DEBOUNCE_MS = 50;        // Button debounce time (ms)
const unsigned long REPEAT_BLOCK_MS = 2000;  // Prevent rapid repeats (ms)
const unsigned long WIFI_RECONNECT_MS = 30000; // WiFi check interval (ms)
const unsigned long HEARTBEAT_INTERVAL = 60000; // Heartbeat (ms)

// ========================================
// SENSOR MAPPING (Button → Sensor ID)
// ========================================

const char* SENSOR_IDS[TOTAL_BUTTONS] = {
    // Row 0 (Buttons 0-5)
    "S_01", "S_02", "S_03", "S_04", "S_05", "S_06",
    // Row 1 (Buttons 6-11)
    "S_07", "S_08", "S_09", "S_10", "S_11", "S_12",
    // Row 2 (Buttons 12-17)
    "S_13", "S_14", "S_15", "S_16", "S_17", "S_18",
    // Row 3 (Buttons 18-23)
    "S_19", "S_20", "S_21", "S_22", "S_23", "S_24",
    // Row 4 (Buttons 24-29)
    "S_25", "S_26", "S_27", "S_28", "S_29", "S_30"
};

// Button labels for serial monitor
const char* BUTTON_LABELS[TOTAL_BUTTONS] = {
    // Row 0 - Corridor 1 (North)
    "C1A-North", "C1B-North", "C1C-North", "C1D-North", "C2A-Left", "C2B-Left",
    // Row 1 - Corridor 3-4 (Right/North Corridor)
    "C3A-Right", "C3B-Right", "C3C-Right", "C3D-Right", "C4A-NCorr", "C4B-ECorr",
    // Row 2 - Corridor 5-6 (Central/South Corridor)
    "C5A-CCorr", "C5B-CCorr", "C6A-SCorr", "C6B-SCorr", "CJ-NW", "CJ-NC",
    // Row 3 - Junction areas (North/Middle)
    "CJ-NE", "CJ-MW", "CJ-MC", "CJ-ME", "CJ-SW", "CJ-SC",
    // Row 4 - Junction/Corridor 7
    "CJ-SE", "C7A-NWSt", "C7B-NESt", "C7C-ESLobby", "STORED", "RESERVED"
};

// ========================================
// STATE VARIABLES
// ========================================

bool buttonStableState[TOTAL_BUTTONS];
bool buttonReadState[TOTAL_BUTTONS];
unsigned long lastStateChange[TOTAL_BUTTONS];
unsigned long lastTriggerTime[TOTAL_BUTTONS];
int currentEmergencyIndex[TOTAL_BUTTONS];

bool wifiConnected = false;
unsigned long lastWiFiCheck = 0;
unsigned long lastHeartbeat = 0;
int connectionFailures = 0;

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
    
    initButtonMatrix();
    initStatusLEDs();
    initBuzzer();
    
    for (int i = 0; i < TOTAL_BUTTONS; i++) {
        buttonStableState[i] = false;
        buttonReadState[i] = false;
        lastStateChange[i] = 0;
        lastTriggerTime[i] = 0;
        currentEmergencyIndex[i] = 0;
    }
    
    connectToWiFi();
    
    if (wifiConnected) {
        registerDevice();
    }
    
    successFeedback();
    
    Serial.println("\n========================================");
    Serial.println("System Ready! Press buttons for alerts.");
    Serial.println("========================================\n");
}

// ========================================
// MAIN LOOP
// ========================================

void loop() {
    unsigned long now = millis();
    
    if (now - lastWiFiCheck > WIFI_RECONNECT_MS) {
        lastWiFiCheck = now;
        checkWiFiConnection();
    }
    
    if (wifiConnected && (now - lastHeartbeat > HEARTBEAT_INTERVAL)) {
        lastHeartbeat = now;
        sendHeartbeat();
    }
    
    scanButtonMatrix();
    
    delay(10);
}

// ========================================
// INITIALIZATION FUNCTIONS
// ========================================

void initButtonMatrix() {
    Serial.println("Initializing 5x6 button matrix...");
    Serial.println("");
    Serial.println("Using ESP32 DevKit V1 (DOIT) pins:");
    Serial.println("  LEFT side: D4, D5, D14, D18, D19 = ROWS");
    Serial.println("  RIGHT side: D13, D21, D22, D23, D25, D26 = COLUMNS");
    Serial.println("");
    
    // Set row pins as OUTPUT
    for (int row = 0; row < ROWS; row++) {
        pinMode(ROW_PINS[row], OUTPUT);
        digitalWrite(ROW_PINS[row], HIGH);
        Serial.printf("  ROW %d → D%d (GPIO %d)\n", row, ROW_PINS[row], ROW_PINS[row]);
    }
    
    // Set column pins as INPUT_PULLUP
    for (int col = 0; col < COLS; col++) {
        pinMode(COL_PINS[col], INPUT_PULLUP);
        Serial.printf("  COL %d → D%d (GPIO %d)\n", col, COL_PINS[col], COL_PINS[col]);
    }
    
    Serial.println("");
    Serial.println("Matrix initialized: 30 buttons ready");
    Serial.println("");
}

void initStatusLEDs() {
    Serial.println("Initializing status LEDs...");
    Serial.println("  D2  = Built-in LED (WiFi status)");
    Serial.println("  D15 = Red LED (Emergency indicator)");
    
    pinMode(LED_BUILTIN, OUTPUT);
    pinMode(LED_RED, OUTPUT);
    
    digitalWrite(LED_BUILTIN, LOW);
    digitalWrite(LED_RED, LOW);
    
    Serial.println("Status LEDs initialized\n");
}

void initBuzzer() {
    Serial.println("Initializing buzzer...");
    Serial.println("  D27 = Buzzer control");
    
    pinMode(BUZZER_PIN, OUTPUT);
    digitalWrite(BUZZER_PIN, LOW);
    
    Serial.println("Buzzer initialized\n");
}

// ========================================
// BUTTON SCANNING
// ========================================

void scanButtonMatrix() {
    unsigned long now = millis();
    
    // Scan each row one at a time
    for (int row = 0; row < ROWS; row++) {
        // Set all rows HIGH (idle)
        setRowsHigh();
        
        // Set current row LOW (active)
        digitalWrite(ROW_PINS[row], LOW);
        delayMicroseconds(100);
        
        // Check each column
        for (int col = 0; col < COLS; col++) {
            int buttonIndex = row * COLS + col;
            
            // Read button state
            // INPUT_PULLUP: LOW = pressed, HIGH = not pressed
            bool pressed = (digitalRead(COL_PINS[col]) == LOW);
            
            // Debouncing: detect change
            if (pressed != buttonReadState[buttonIndex]) {
                buttonReadState[buttonIndex] = pressed;
                lastStateChange[buttonIndex] = now;
            }
            
            // Check if stable
            bool stable = (now - lastStateChange[buttonIndex]) >= DEBOUNCE_MS;
            
            if (stable && buttonStableState[buttonIndex] != buttonReadState[buttonIndex]) {
                buttonStableState[buttonIndex] = buttonReadState[buttonIndex];
                
                // Button just pressed
                if (buttonStableState[buttonIndex]) {
                    handleButtonPress(buttonIndex, now);
                }
            }
        }
        
        // Reset row to HIGH
        digitalWrite(ROW_PINS[row], HIGH);
    }
}

void setRowsHigh() {
    for (int row = 0; row < ROWS; row++) {
        digitalWrite(ROW_PINS[row], HIGH);
    }
}

void handleButtonPress(int buttonIndex, unsigned long now) {
    // Prevent rapid repeats
    if (now - lastTriggerTime[buttonIndex] < REPEAT_BLOCK_MS) {
        Serial.printf("[Button %d] Rate limited\n", buttonIndex);
        return;
    }
    
    lastTriggerTime[buttonIndex] = now;
    
    // Cycle emergency type
    currentEmergencyIndex[buttonIndex] = (currentEmergencyIndex[buttonIndex] + 1) % NUM_EMERGENCY_TYPES;
    const char* emergencyType = EMERGENCY_TYPES[currentEmergencyIndex[buttonIndex]];
    
    const char* sensorId = SENSOR_IDS[buttonIndex];
    const char* buttonLabel = BUTTON_LABELS[buttonIndex];
    
    totalTriggers++;
    
    // Print to Serial Monitor
    Serial.println("");
    Serial.println("========================================");
    Serial.println("  EMERGENCY TRIGGERED!");
    Serial.println("========================================");
    Serial.printf("  Button #: %d (%s)\n", buttonIndex, buttonLabel);
    Serial.printf("  Sensor ID: %s\n", sensorId);
    Serial.printf("  Type: %s\n", emergencyType);
    Serial.printf("  Total triggers: %lu\n", totalTriggers);
    Serial.println("========================================\n");
    
    // Feedback
    emergencyFeedback();
    
    // Send to server
    if (wifiConnected) {
        sendEmergencyToAPI(sensorId, emergencyType);
    } else {
        Serial.println("[ERROR] WiFi not connected");
        failedSends++;
    }
    
    printStatistics();
}

// ========================================
// STATUS LED FUNCTIONS
// ========================================

void emergencyFeedback() {
    // Flash red LED and buzzer 3 times
    for (int i = 0; i < 3; i++) {
        digitalWrite(LED_RED, HIGH);
        digitalWrite(BUZZER_PIN, HIGH);
        delay(100);
        digitalWrite(LED_RED, LOW);
        digitalWrite(BUZZER_PIN, LOW);
        delay(50);
    }
}

void successFeedback() {
    digitalWrite(LED_BUILTIN, HIGH);
    digitalWrite(BUZZER_PIN, HIGH);
    delay(200);
    digitalWrite(LED_BUILTIN, LOW);
    digitalWrite(BUZZER_PIN, LOW);
}

// ========================================
// WIFI FUNCTIONS
// ========================================

void connectToWiFi() {
    Serial.println("========================================");
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
        digitalWrite(LED_BUILTIN, !digitalRead(LED_BUILTIN));
        attempts++;
    }
    
    Serial.println();
    
    if (WiFi.status() == WL_CONNECTED) {
        wifiConnected = true;
        connectionFailures = 0;
        
        Serial.println("========================================");
        Serial.println("WiFi Connected!");
        Serial.println("========================================");
        Serial.printf("IP Address: %s\n", WiFi.localIP().toString().c_str());
        Serial.printf("Signal Strength: %d dBm\n", WiFi.RSSI());
        Serial.printf("MAC Address: %s\n", WiFi.macAddress().c_str());
        Serial.println("========================================\n");
        
        digitalWrite(LED_BUILTIN, HIGH);
        
    } else {
        wifiConnected = false;
        
        Serial.println("========================================");
        Serial.println("WiFi Connection Failed!");
        Serial.println("========================================");
        Serial.println("Will retry automatically...\n");
    }
}

void checkWiFiConnection() {
    if (WiFi.status() != WL_CONNECTED) {
        if (wifiConnected) {
            wifiConnected = false;
            Serial.println("[WiFi] Connection lost!");
            digitalWrite(LED_BUILTIN, LOW);
            connectionFailures++;
            
            if (connectionFailures >= 3) {
                Serial.println("[WiFi] Attempting reconnection...");
                connectToWiFi();
                if (wifiConnected) {
                    connectionFailures = 0;
                    registerDevice();
                }
            }
        }
    } else {
        if (!wifiConnected) {
            wifiConnected = true;
            connectionFailures = 0;
            Serial.println("[WiFi] Reconnected!");
            digitalWrite(LED_BUILTIN, HIGH);
            registerDevice();
        }
    }
}

// ========================================
// HTTP COMMUNICATION
// ========================================

void registerDevice() {
    if (!wifiConnected) return;
    
    Serial.println("[API] Registering device...");
    
    HTTPClient http;
    String url = String(API_HOST) + "/esp32/register";
    
    http.begin(url);
    http.addHeader("Content-Type", "application/json");
    http.setTimeout(5000);
    
    StaticJsonDocument<256> doc;
    doc["device_id"] = DEVICE_ID;
    doc["location"] = DEVICE_LOCATION;
    doc["ip_address"] = WiFi.localIP().toString();
    doc["wifi_ssid"] = WIFI_SSID;
    doc["button_count"] = TOTAL_BUTTONS;
    doc["firmware_version"] = "2.1";
    
    String payload;
    serializeJson(doc, payload);
    
    int httpCode = http.POST(payload);
    
    if (httpCode == 200 || httpCode == 201) {
        Serial.println("[API] Device registered!");
    } else {
        Serial.printf("[API] Registration failed: HTTP %d\n", httpCode);
    }
    
    http.end();
}

void sendEmergencyToAPI(const char* sensorId, const char* emergencyType) {
    Serial.println("[API] Sending emergency...");
    
    HTTPClient http;
    String url = String(API_HOST) + "/sensor-update";
    
    http.begin(url);
    http.addHeader("Content-Type", "application/json");
    http.setTimeout(5000);
    
    StaticJsonDocument<256> doc;
    doc["sensor_id"] = sensorId;
    doc["type"] = emergencyType;
    doc["device_id"] = DEVICE_ID;
    doc["source"] = "esp32";
    
    String payload;
    serializeJson(doc, payload);
    
    unsigned long startTime = millis();
    int httpCode = http.POST(payload);
    unsigned long responseTime = millis() - startTime;
    
    if (httpCode > 0) {
        String response = http.getString();
        Serial.printf("[API] Success! (%lums) HTTP %d\n", responseTime, httpCode);
        successfulSends++;
    } else {
        Serial.printf("[API] Failed: %s\n", http.errorToString(httpCode).c_str());
        failedSends++;
    }
    
    http.end();
}

void sendHeartbeat() {
    if (!wifiConnected) return;
    
    HTTPClient http;
    String url = String(API_HOST) + "/esp32/heartbeat";
    
    http.begin(url);
    http.addHeader("Content-Type", "application/json");
    http.setTimeout(3000);
    
    StaticJsonDocument<128> doc;
    doc["device_id"] = DEVICE_ID;
    doc["rssi"] = WiFi.RSSI();
    doc["uptime_ms"] = millis();
    doc["total_triggers"] = totalTriggers;
    
    String payload;
    serializeJson(doc, payload);
    
    int httpCode = http.POST(payload);
    
    if (httpCode == 200) {
        digitalWrite(LED_BUILTIN, HIGH);
    }
    
    http.end();
}

// ========================================
// UTILITY FUNCTIONS
// ========================================

void printHeader() {
    Serial.println("");
    Serial.println("╔═══════════════════════════════════════════════════════════════╗");
    Serial.println("║                                                               ║");
    Serial.println("║   ESP32 SMART EVACUATION CONTROLLER v2.1                     ║");
    Serial.println("║   30-Button Emergency Matrix + WiFi                         ║");
    Serial.println("║                                                               ║");
    Serial.println("║   Board: ESP32 DevKit V1 (DOIT)                             ║");
    Serial.println("║   Layout: 5x6 Matrix (30 buttons)                           ║");
    Serial.println("║   Connectivity: WiFi (HTTP)                                ║");
    Serial.println("║                                                               ║");
    Serial.println("╚═══════════════════════════════════════════════════════════════╝");
    Serial.println("");
}

void printStatistics() {
    Serial.println("--- Statistics ---");
    Serial.printf("  Triggers: %lu | Success: %lu | Failed: %lu\n", 
                  totalTriggers, successfulSends, failedSends);
    if (totalTriggers > 0) {
        float rate = (successfulSends * 100.0) / totalTriggers;
        Serial.printf("  Success Rate: %.1f%%\n", rate);
    }
    if (WiFi.status() == WL_CONNECTED) {
        Serial.printf("  WiFi RSSI: %d dBm\n", WiFi.RSSI());
    }
    Serial.println("");
}
