# Wokwi Test Sketch - Button Matrix Only
# Use this to test button wiring without WiFi/API

// ============================================
// WOKWI TEST - 30 BUTTON MATRIX
// Copy this to sketch.ino in Wokwi
// ============================================

#include <Arduino.h>

// Button Matrix Pins
const int ROW_PINS[5] = {4, 5, 6, 7, 8};   // GPIO 4-8 (OUTPUT)
const int COL_PINS[6] = {9, 10, 11, 12, 13, 14}; // GPIO 9-14 (INPUT_PULLUP)

// Status LEDs
const int LED_RED = 15;
const int LED_YELLOW = 16;
const int LED_GREEN = 17;

// Last button state
int lastButton = -1;
unsigned long lastPressTime = 0;

void setup() {
  Serial.begin(115200);
  Serial.println("=== ESP32 Button Matrix Test ===");
  
  // Initialize Row pins as OUTPUT
  for (int i = 0; i < 5; i++) {
    pinMode(ROW_PINS[i], OUTPUT);
    digitalWrite(ROW_PINS[i], HIGH); // Start HIGH (inactive)
  }
  
  // Initialize Column pins as INPUT_PULLUP
  for (int i = 0; i < 6; i++) {
    pinMode(COL_PINS[i], INPUT_PULLUP);
  }
  
  // Initialize LED pins as OUTPUT
  pinMode(LED_RED, OUTPUT);
  pinMode(LED_YELLOW, OUTPUT);
  pinMode(LED_GREEN, OUTPUT);
  
  // Turn all LEDs off
  digitalWrite(LED_RED, LOW);
  digitalWrite(LED_YELLOW, LOW);
  digitalWrite(LED_GREEN, LOW);
  
  Serial.println("Matrix initialized. Press buttons to test...");
  Serial.println("Button mapping: Row x 6 + Column = Button Number");
}

void loop() {
  int buttonPressed = scanMatrix();
  
  if (buttonPressed >= 0) {
    if (buttonPressed != lastButton) {
      lastButton = buttonPressed;
      lastPressTime = millis();
      
      Serial.print("Button pressed: ");
      Serial.println(buttonPressed);
      
      // Show which corridor and cycle type
      int corridor = buttonPressed / 6 + 1;
      int col = buttonPressed % 6;
      
      Serial.print("Corridor: C");
      Serial.print(corridor);
      Serial.print(col == 0 ? "A" : (col < 4 ? "B" : "C"));
      Serial.print(" (Button ");
      Serial.print(buttonPressed);
      Serial.println(")");
      
      // Light up LEDs based on button number
      flashLEDs(buttonPressed);
    }
  }
  
  // Clear lastButton if held too long (debounce)
  if (lastButton >= 0 && millis() - lastPressTime > 500) {
    lastButton = -1;
  }
}

int scanMatrix() {
  // Scan each row
  for (int row = 0; row < 5; row++) {
    // Set current row LOW, others HIGH
    for (int i = 0; i < 5; i++) {
      digitalWrite(ROW_PINS[i], (i == row) ? LOW : HIGH);
    }
    
    delayMicroseconds(100); // Small delay for signal settle
    
    // Check each column
    for (int col = 0; col < 6; col++) {
      if (digitalRead(COL_PINS[col]) == LOW) {
        // Button is pressed: row x 6 + col
        return row * 6 + col;
      }
    }
  }
  
  return -1; // No button pressed
}

void flashLEDs(int buttonNum) {
  // Flash all LEDs in sequence based on button number
  
  // Red LED
  digitalWrite(LED_RED, HIGH);
  delay(100);
  digitalWrite(LED_RED, LOW);
  
  // Yellow LED  
  digitalWrite(LED_YELLOW, HIGH);
  delay(100);
  digitalWrite(LED_YELLOW, LOW);
  
  // Green LED
  digitalWrite(LED_GREEN, HIGH);
  delay(100);
  digitalWrite(LED_GREEN, LOW);
  
  // Flash faster based on button number
  for (int i = 0; i < (buttonNum % 5); i++) {
    digitalWrite(LED_YELLOW, HIGH);
    delay(50);
    digitalWrite(LED_YELLOW, LOW);
    delay(50);
  }
}
