/*
  arduino_code.ino - Smart Emergency Evacuation IoT Sensor
  ==========================================================
  
  This Arduino reads smoke & flame sensors and sends data
  to the computer via USB (Serial port).
  
  Think of it like:
  - The smoke sensor is like your nose (smells smoke)
  - The flame sensor is like your eyes (sees fire)
  - Arduino sends what it detects to the computer
  
  WIRING GUIDE:
  =============
  
  MQ-2 Smoke Sensor:
  ┌─────────────────────────────────────────┐
  │  MQ-2 Pin    →  Arduino Pin             │
  │  VCC         →  5V                      │
  │  GND         →  GND                     │
  │  A0 (analog) →  A0 (reads smoke level)  │
  │  D0 (digital)→  Not used (optional)     │
  └─────────────────────────────────────────┘
  
  Flame Sensor (IR):
  ┌─────────────────────────────────────────┐
  │  Flame Pin   →  Arduino Pin             │
  │  VCC         →  5V                      │
  │  GND         →  GND                     │
  │  D0 (digital)→  D2 (1=fire, 0=no fire)  │
  └─────────────────────────────────────────┘
  
  LED Indicators (optional but helpful):
  ┌─────────────────────────────────────────┐
  │  Red LED (+) →  D13 (fire alert)        │
  │  Red LED (-) →  GND (through 220Ω)     │
  └─────────────────────────────────────────┘
  
  NOTE: If you have 4 sensors (one per room), duplicate
  this code for sensors labeled sensor_1 to sensor_4.
*/

// ============================================================
// PIN DEFINITIONS
// ============================================================
const int SMOKE_PIN   = A0;   // MQ-2 analog output
const int FLAME_PIN   = 2;    // Flame sensor digital output
const int LED_PIN     = 13;   // Built-in LED (fire alert)

// ============================================================
// SETTINGS
// ============================================================
const String SENSOR_ID     = "sensor_1";  // Change for each Arduino
const int    SMOKE_THRESHOLD = 300;        // Values above = heavy smoke
const int    SEND_INTERVAL   = 1000;       // Send data every 1 second
const int    BAUD_RATE        = 9600;      // Must match serial_reader.py

// ============================================================
// VARIABLES
// ============================================================
int  smokeValue  = 0;    // 0-1023 (higher = more smoke)
int  flameValue  = 0;    // 0 = fire, 1 = no fire (inverted!)
bool fireAlert   = false;
unsigned long lastSend = 0;

// ============================================================
void setup() {
  // Start serial communication (USB to computer)
  Serial.begin(BAUD_RATE);
  
  // Set pin modes
  pinMode(FLAME_PIN, INPUT);
  pinMode(LED_PIN, OUTPUT);
  
  // Wait for serial to be ready
  delay(1000);
  
  Serial.println("=== Smart Evacuation Sensor Ready ===");
  Serial.print("Sensor ID: ");
  Serial.println(SENSOR_ID);
  Serial.println("Format: SENSOR:id,SMOKE:value,FLAME:value");
  Serial.println("=====================================");
}

// ============================================================
void loop() {
  // Read sensors
  smokeValue = analogRead(SMOKE_PIN);   // 0-1023
  
  // Flame sensor: LOW (0) = fire detected, HIGH (1) = no fire
  // We INVERT it so: flameValue=1 means fire, flameValue=0 means no fire
  flameValue = (digitalRead(FLAME_PIN) == LOW) ? 1 : 0;
  
  // Determine alert status
  fireAlert = (flameValue == 1) || (smokeValue > SMOKE_THRESHOLD);
  
  // Flash LED if fire detected
  if (fireAlert) {
    // Blink LED rapidly to signal danger
    digitalWrite(LED_PIN, HIGH);
    delay(100);
    digitalWrite(LED_PIN, LOW);
    delay(100);
  } else {
    digitalWrite(LED_PIN, LOW);  // LED off when safe
  }
  
  // Send data to computer every SEND_INTERVAL milliseconds
  unsigned long now = millis();
  if (now - lastSend >= SEND_INTERVAL) {
    sendSensorData();
    lastSend = now;
  }
}

// ============================================================
void sendSensorData() {
  /*
   * Send formatted message to computer via USB Serial.
   * Python's serial_reader.py will read this!
   * 
   * Format: SENSOR:sensor_1,SMOKE:450,FLAME:1
   */
  
  Serial.print("SENSOR:");
  Serial.print(SENSOR_ID);
  Serial.print(",SMOKE:");
  Serial.print(smokeValue);
  Serial.print(",FLAME:");
  Serial.println(flameValue);
  
  // Also print human-readable version (for debugging)
  if (fireAlert) {
    Serial.print("⚠️  ALERT! Smoke=");
    Serial.print(smokeValue);
    if (flameValue == 1) {
      Serial.print(" | FLAME DETECTED!");
    }
    Serial.println();
  }
}

/*
  UNDERSTANDING SENSOR VALUES:
  ============================
  
  MQ-2 Smoke Sensor (Analog value 0-1023):
  - 0   to 100  = Very clean air (normal)
  - 100 to 200  = Slight pollution
  - 200 to 300  = Moderate smoke
  - 300 to 500  = Heavy smoke (danger!)
  - 500 to 1023 = Extreme smoke/gas (evacuate!)
  
  Flame Sensor (Digital):
  - 0 = No flame detected
  - 1 = Flame/Fire detected!
  
  Note: MQ-2 needs 2-3 minutes to warm up after power on.
  The first readings may be inaccurate.
*/
