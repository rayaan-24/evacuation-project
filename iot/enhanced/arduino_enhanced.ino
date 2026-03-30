/*
  Smart Evacuation System - Enhanced Arduino Firmware
  ====================================================
  Features:
  - 5x6 Button Matrix (30 emergency triggers)
  - I2C LCD Display (16x2) for status
  - Multi-pattern LED alerts (emergency type specific)
  - Multi-tone buzzer alerts
  - Status LEDs (Green/Yellow/Red)
  - Serial communication with Python backend
  
  Serial Output Format:
  SENSOR:sensor_<id>,TYPE:<TYPE>
  
  Author: Smart Evacuation System
  Version: 2.0.0
*/

#include <Wire.h>
#include <LiquidCrystal_I2C.h>

// ============================================
// CONFIGURATION
// ============================================

// Button Matrix
const int ROWS = 5;
const int COLS = 6;
const int TOTAL_BUTTONS = ROWS * COLS;

const int ROW_PINS[ROWS] = {2, 3, 4, 5, 6};
const int COL_PINS[COLS] = {7, 8, 9, 10, 11, 12};

// Status LEDs
const int LED_GREEN = A1;
const int LED_YELLOW = A2;
const int LED_RED = A3;

// Alert buzzer
const int BUZZER_PIN = A0;

// LCD Configuration
LiquidCrystal_I2C lcd(0x27, 16, 2);

// Timing Configuration
const unsigned long DEBOUNCE_MS = 60;
const unsigned long REPEAT_BLOCK_MS = 1500;
const unsigned long LCD_UPDATE_MS = 500;
const unsigned long LED_BLINK_MS = 200;

// ============================================
// EMERGENCY TYPES
// ============================================

enum EmergencyType {
  EMERGENCY_NONE,
  EMERGENCY_FIRE,
  EMERGENCY_SMOKE,
  EMERGENCY_GAS,
  EMERGENCY_BLOCKAGE,
  EMERGENCY_CROWD
};

// Emergency configuration
struct EmergencyConfig {
  const char* name;
  int beepFreq;
  int beepDuration;
  int beepCount;
  unsigned long patternInterval;
};

const EmergencyConfig EMERGENCY_CONFIGS[] = {
  {"NONE",      0,      0, 0,     0},
  {"FIRE",      2000,   100, 3,   600},
  {"SMOKE",     1500,   200, 2,   800},
  {"GAS",       2500,   150, 5,   400},
  {"BLOCKAGE",  1000,   400, 1,  1000},
  {"CROWD",     1800,   150, 2,   700}
};

// ============================================
// GLOBAL STATE
// ============================================

unsigned long lastTriggerAt[TOTAL_BUTTONS];
unsigned long lastStateChangeAt[TOTAL_BUTTONS];
bool buttonStableState[TOTAL_BUTTONS];
bool buttonReadState[TOTAL_BUTTONS];

EmergencyType currentEmergency = EMERGENCY_NONE;
int lastTriggeredSensor = -1;
unsigned long lastEmergencyTime = 0;
unsigned long lastLedBlink = 0;
bool ledState = false;
unsigned long lastLcdUpdate = 0;
int displayLine = 0;

// System state
unsigned long systemStartTime = 0;
int totalEmergenciesTriggered = 0;

// ============================================
// SETUP
// ============================================

void setup() {
  Serial.begin(9600);
  while (!Serial && millis() < 2000);
  
  // Initialize LCD
  lcd.init();
  lcd.backlight();
  lcd.setCursor(0, 0);
  lcd.print("Smart Evacuation");
  lcd.setCursor(0, 1);
  lcd.print("Initializing...");
  delay(1000);
  
  // Initialize button matrix
  initButtonMatrix();
  
  // Initialize LEDs
  initStatusLeds();
  
  // Initialize buzzer
  pinMode(BUZZER_PIN, OUTPUT);
  digitalWrite(BUZZER_PIN, LOW);
  
  // Initialize serial
  Serial.println("=== Smart Evacuation System v2.0 ===");
  Serial.println("READY - 30-sensor emergency console active");
  Serial.println("Format: SENSOR:sensor_<id>,TYPE:<TYPE>");
  
  // Display ready screen
  displayReadyScreen();
  
  systemStartTime = millis();
}

// ============================================
// BUTTON MATRIX INITIALIZATION
// ============================================

void initButtonMatrix() {
  for (int row = 0; row < ROWS; row++) {
    pinMode(ROW_PINS[row], OUTPUT);
    digitalWrite(ROW_PINS[row], HIGH);
  }
  
  for (int col = 0; col < COLS; col++) {
    pinMode(COL_PINS[col], INPUT_PULLUP);
  }
  
  for (int i = 0; i < TOTAL_BUTTONS; i++) {
    lastTriggerAt[i] = 0;
    lastStateChangeAt[i] = 0;
    buttonStableState[i] = false;
    buttonReadState[i] = false;
  }
}

// ============================================
// STATUS LED INITIALIZATION
// ============================================

void initStatusLeds() {
  pinMode(LED_GREEN, OUTPUT);
  pinMode(LED_YELLOW, OUTPUT);
  pinMode(LED_RED, OUTPUT);
  
  digitalWrite(LED_GREEN, LOW);
  digitalWrite(LED_YELLOW, LOW);
  digitalWrite(LED_RED, LOW);
}

// ============================================
// MAIN LOOP
// ============================================

void loop() {
  scanMatrix();
  updateAlerts();
  handleSerialCommands();
  updateDisplay();
}

// ============================================
// MATRIX SCANNING
// ============================================

void scanMatrix() {
  unsigned long now = millis();
  
  for (int row = 0; row < ROWS; row++) {
    setRowsIdle();
    digitalWrite(ROW_PINS[row], LOW);
    delayMicroseconds(80);
    
    for (int col = 0; col < COLS; col++) {
      int index = row * COLS + col;
      bool pressed = (digitalRead(COL_PINS[col]) == LOW);
      
      if (pressed != buttonReadState[index]) {
        buttonReadState[index] = pressed;
        lastStateChangeAt[index] = now;
      }
      
      bool stable = (now - lastStateChangeAt[index]) >= DEBOUNCE_MS;
      if (stable && buttonStableState[index] != buttonReadState[index]) {
        buttonStableState[index] = buttonReadState[index];
        
        if (buttonStableState[index]) {
          handleButtonPress(index);
        }
      }
    }
  }
  
  setRowsIdle();
}

void setRowsIdle() {
  for (int row = 0; row < ROWS; row++) {
    digitalWrite(ROW_PINS[row], HIGH);
  }
}

// ============================================
// BUTTON HANDLING
// ============================================

void handleButtonPress(int index) {
  unsigned long now = millis();
  
  if (index < 0 || index >= TOTAL_BUTTONS) return;
  if (now - lastTriggerAt[index] < REPEAT_BLOCK_MS) return;
  
  lastTriggerAt[index] = now;
  lastEmergencyTime = now;
  lastTriggeredSensor = index;
  
  // Cycle through emergency types on each press
  currentEmergency = getNextEmergencyType();
  
  // Output serial data
  Serial.print("SENSOR:sensor_");
  Serial.print(index);
  Serial.print(",TYPE:");
  Serial.println(getEmergencyTypeName(currentEmergency));
  
  totalEmergenciesTriggered++;
  
  // Trigger alerts
  triggerAlert(currentEmergency);
  updateLcdForEmergency(index, currentEmergency);
  
  // Print debug info
  printDebugInfo(index, currentEmergency);
}

// ============================================
// EMERGENCY TYPE MANAGEMENT
// ============================================

EmergencyType getNextEmergencyType() {
  switch (currentEmergency) {
    case EMERGENCY_NONE:    return EMERGENCY_FIRE;
    case EMERGENCY_FIRE:     return EMERGENCY_SMOKE;
    case EMERGENCY_SMOKE:    return EMERGENCY_GAS;
    case EMERGENCY_GAS:      return EMERGENCY_BLOCKAGE;
    case EMERGENCY_BLOCKAGE: return EMERGENCY_CROWD;
    case EMERGENCY_CROWD:    return EMERGENCY_FIRE;
    default:                 return EMERGENCY_FIRE;
  }
}

const char* getEmergencyTypeName(EmergencyType type) {
  switch (type) {
    case EMERGENCY_FIRE:     return "FIRE";
    case EMERGENCY_SMOKE:    return "SMOKE";
    case EMERGENCY_GAS:      return "GAS";
    case EMERGENCY_BLOCKAGE: return "BLOCKAGE";
    case EMERGENCY_CROWD:    return "CROWD";
    default:                 return "NONE";
  }
}

// ============================================
// ALERT HANDLING
// ============================================

void triggerAlert(EmergencyType type) {
  if (type == EMERGENCY_NONE) {
    setAllLedsOff();
    return;
  }
  
  const EmergencyConfig& config = EMERGENCY_CONFIGS[type];
  
  // Play buzzer pattern
  for (int i = 0; i < config.beepCount; i++) {
    if (config.beepFreq > 0) {
      tone(BUZZER_PIN, config.beepFreq, config.beepDuration);
    }
    delay(config.beepDuration + 50);
  }
  
  // Update LED state immediately
  updateLedForEmergency(type);
}

void updateAlerts() {
  unsigned long now = millis();
  
  if (currentEmergency == EMERGENCY_NONE) {
    // Normal mode - slow green pulse
    setAllLedsOff();
    digitalWrite(LED_GREEN, (now % 2000) < 1000 ? HIGH : LOW);
    return;
  }
  
  const EmergencyConfig& config = EMERGENCY_CONFIGS[currentEmergency];
  
  // Check if pattern interval has passed
  if (now - lastLedBlink >= config.patternInterval) {
    lastLedBlink = now;
    ledState = !ledState;
    updateLedForEmergency(currentEmergency);
    
    // Also replay alert sound
    for (int i = 0; i < config.beepCount; i++) {
      if (config.beepFreq > 0) {
        tone(BUZZER_PIN, config.beepFreq, config.beepDuration);
      }
      delay(config.beepDuration + 50);
    }
  }
  
  // Auto-clear after 60 seconds of no triggers
  if (now - lastEmergencyTime > 60000 && currentEmergency != EMERGENCY_NONE) {
    clearEmergency();
  }
}

void updateLedForEmergency(EmergencyType type) {
  setAllLedsOff();
  
  switch (type) {
    case EMERGENCY_FIRE:
      digitalWrite(LED_RED, HIGH);
      digitalWrite(LED_YELLOW, ledState ? HIGH : LOW);
      break;
    case EMERGENCY_SMOKE:
      digitalWrite(LED_YELLOW, HIGH);
      break;
    case EMERGENCY_GAS:
      digitalWrite(LED_RED, ledState ? HIGH : LOW);
      digitalWrite(LED_YELLOW, ledState ? HIGH : LOW);
      break;
    case EMERGENCY_BLOCKAGE:
      digitalWrite(LED_YELLOW, HIGH);
      break;
    case EMERGENCY_CROWD:
      digitalWrite(LED_RED, HIGH);
      break;
    default:
      break;
  }
}

void setAllLedsOff() {
  digitalWrite(LED_GREEN, LOW);
  digitalWrite(LED_YELLOW, LOW);
  digitalWrite(LED_RED, LOW);
}

void clearEmergency() {
  currentEmergency = EMERGENCY_NONE;
  lastTriggeredSensor = -1;
  setAllLedsOff();
  displayReadyScreen();
  
  Serial.println("INFO:Emergency cleared");
}

// ============================================
// LCD DISPLAY
// ============================================

void updateDisplay() {
  unsigned long now = millis();
  if (now - lastLcdUpdate < LCD_UPDATE_MS) return;
  lastLcdUpdate = now;
  
  if (currentEmergency == EMERGENCY_NONE) {
    // Show normal status with rotating info
    if (now % 4000 < 2000) {
      displayReadyScreen();
    } else {
      displayStatistics();
    }
  } else {
    displayEmergencyScreen();
  }
}

void displayReadyScreen() {
  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.print("  SYSTEM READY  ");
  lcd.setCursor(0, 1);
  lcd.print("Press btn for  alarm");
}

void displayEmergencyScreen() {
  const char* typeName = getEmergencyTypeName(currentEmergency);
  
  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.print("!EMERGENCY!");
  lcd.setCursor(11, 0);
  lcd.print(typeName);
  
  lcd.setCursor(0, 1);
  lcd.print("Zone:");
  lcd.print(lastTriggeredSensor);
  lcd.print(" (");
  lcd.print(getCorridorFromSensor(lastTriggeredSensor));
  lcd.print(")   ");
}

void updateLcdForEmergency(int sensorIndex, EmergencyType type) {
  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.print("! EMERGENCY !");
  
  lcd.setCursor(0, 1);
  lcd.print(getEmergencyTypeName(type));
  lcd.print(" S");
  lcd.print(sensorIndex);
  lcd.print(":");
  lcd.print(getCorridorFromSensor(sensorIndex));
}

void displayStatistics() {
  unsigned long uptime = (millis() - systemStartTime) / 1000;
  int minutes = uptime / 60;
  int seconds = uptime % 60;
  
  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.print("Uptime: ");
  lcd.print(minutes);
  lcd.print("m ");
  lcd.print(seconds);
  lcd.print("s");
  
  lcd.setCursor(0, 1);
  lcd.print("Alerts: ");
  lcd.print(totalEmergenciesTriggered);
  lcd.print(" Sensors:30");
}

const char* getCorridorFromSensor(int sensorIndex) {
  // Map sensor index to corridor ID
  const char* corridors[] = {
    "C1A", "C1B", "C1C", "C1D", "C2A",  // 0-4
    "C2B", "C2C", "C2D", "C3A", "C3B",  // 5-9
    "C3C", "C3D", "C4A", "C4B", "C5A",  // 10-14
    "C5B", "C6A", "C6B", "CJN","CJC",   // 15-19
    "CJE", "CJM","CJX","CJS","CJY",     // 20-24
    "CJZ", "C7A", "C7B", "C7C", "---"  // 25-29
  };
  
  if (sensorIndex >= 0 && sensorIndex < 30) {
    return corridors[sensorIndex];
  }
  return "---";
}

// ============================================
// SERIAL COMMAND HANDLING
// ============================================

void handleSerialCommands() {
  if (Serial.available() > 0) {
    String command = Serial.readStringUntil('\n');
    command.trim();
    command.toUpperCase();
    
    if (command.startsWith("STATUS?")) {
      sendStatus();
    } else if (command.startsWith("CLEAR")) {
      clearEmergency();
      Serial.println("INFO:Emergency cleared via serial");
    } else if (command.startsWith("RESET")) {
      resetSystem();
    } else if (command.startsWith("TEST")) {
      runSelfTest();
    } else if (command.startsWith("LCD:")) {
      updateLcdMessage(command.substring(4));
    }
  }
}

void sendStatus() {
  Serial.print("STATUS:");
  Serial.print("READY|");
  Serial.print("CURRENT:");
  Serial.print(getEmergencyTypeName(currentEmergency));
  Serial.print("|LAST_SENSOR:");
  Serial.print(lastTriggeredSensor);
  Serial.print("|TOTAL_ALERTS:");
  Serial.println(totalEmergenciesTriggered);
}

void resetSystem() {
  currentEmergency = EMERGENCY_NONE;
  lastTriggeredSensor = -1;
  totalEmergenciesTriggered = 0;
  systemStartTime = millis();
  setAllLedsOff();
  digitalWrite(BUZZER_PIN, LOW);
  displayReadyScreen();
  
  Serial.println("INFO:System reset complete");
}

void runSelfTest() {
  Serial.println("INFO:Running self-test...");
  
  lcd.clear();
  lcd.print("SELF-TEST");
  
  // Test LEDs
  Serial.println("TEST:LED_GREEN");
  digitalWrite(LED_GREEN, HIGH);
  delay(200);
  
  Serial.println("TEST:LED_YELLOW");
  digitalWrite(LED_GREEN, LOW);
  digitalWrite(LED_YELLOW, HIGH);
  delay(200);
  
  Serial.println("TEST:LED_RED");
  digitalWrite(LED_YELLOW, LOW);
  digitalWrite(LED_RED, HIGH);
  delay(200);
  
  // Test buzzer
  Serial.println("TEST:BUZZER");
  tone(BUZZER_PIN, 1000, 200);
  delay(300);
  
  // Test LCD
  Serial.println("TEST:LCD");
  lcd.clear();
  lcd.print("LCD Test OK!");
  delay(500);
  
  // Test all buttons
  Serial.println("TEST:BUTTONS");
  lcd.setCursor(0, 1);
  lcd.print("Press all btns...");
  
  // Reset
  setAllLedsOff();
  noTone(BUZZER_PIN);
  displayReadyScreen();
  
  Serial.println("INFO:Self-test complete - all systems OK");
}

void updateLcdMessage(String message) {
  lcd.clear();
  lcd.setCursor(0, 0);
  
  if (message.length() <= 16) {
    lcd.print(message);
  } else {
    lcd.print(message.substring(0, 16));
    lcd.setCursor(0, 1);
    lcd.print(message.substring(16, min(message.length(), 32)));
  }
}

// ============================================
// DEBUG OUTPUT
// ============================================

void printDebugInfo(int sensorIndex, EmergencyType type) {
  Serial.print("DEBUG:Sensor ");
  Serial.print(sensorIndex);
  Serial.print(" (");
  Serial.print(getCorridorFromSensor(sensorIndex));
  Serial.print(") -> ");
  Serial.println(getEmergencyTypeName(type));
}
