/*
  arduino_code.ino - 5x6 button matrix emergency trigger (30 corridors)

  Output format to serial:
  SENSOR:sensor_<id>,TYPE:FIRE

  Each button corresponds to one corridor sensor in the backend sensor_map.
*/

const int ROWS = 5;
const int COLS = 6;
const int TOTAL_BUTTONS = ROWS * COLS;

// Update pins to match your board wiring.
const int ROW_PINS[ROWS] = {2, 3, 4, 5, 6};
const int COL_PINS[COLS] = {7, 8, 9, 10, 11, 12};

const int LED_PIN = 13;
const int BUZZER_PIN = A0;

const unsigned long DEBOUNCE_MS = 60;
const unsigned long REPEAT_BLOCK_MS = 1200;
const bool ENABLE_BUZZER = true;

unsigned long lastTriggerAt[TOTAL_BUTTONS];
unsigned long lastStateChangeAt[TOTAL_BUTTONS];
bool buttonStableState[TOTAL_BUTTONS];
bool buttonReadState[TOTAL_BUTTONS];


void setup() {
  Serial.begin(9600);

  for (int row = 0; row < ROWS; row++) {
    pinMode(ROW_PINS[row], OUTPUT);
    digitalWrite(ROW_PINS[row], HIGH);
  }

  for (int col = 0; col < COLS; col++) {
    pinMode(COL_PINS[col], INPUT_PULLUP);
  }

  pinMode(LED_PIN, OUTPUT);
  digitalWrite(LED_PIN, LOW);

  pinMode(BUZZER_PIN, OUTPUT);
  digitalWrite(BUZZER_PIN, LOW);

  for (int i = 0; i < TOTAL_BUTTONS; i++) {
    lastTriggerAt[i] = 0;
    lastStateChangeAt[i] = 0;
    buttonStableState[i] = false;
    buttonReadState[i] = false;
  }

  Serial.println("=== 30-Sensor Matrix Emergency Console Ready ===");
  Serial.println("Message format: SENSOR:sensor_<id>,TYPE:FIRE");
  Serial.println("Rows: 5, Cols: 6, Total buttons: 30");
}


void loop() {
  scanMatrix();
}


void scanMatrix() {
  unsigned long now = millis();

  for (int row = 0; row < ROWS; row++) {
    // Drive current row low and keep others high.
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
          handleButtonPress(index, now);
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


void handleButtonPress(int index, unsigned long now) {
  if (index < 0 || index >= TOTAL_BUTTONS) {
    return;
  }

  if (now - lastTriggerAt[index] < REPEAT_BLOCK_MS) {
    return;
  }

  lastTriggerAt[index] = now;

  Serial.print("SENSOR:sensor_");
  Serial.print(index);
  Serial.println(",TYPE:FIRE");

  blinkAlert();
}


void blinkAlert() {
  digitalWrite(LED_PIN, HIGH);

  if (ENABLE_BUZZER) {
    tone(BUZZER_PIN, 2000, 120);
  }

  delay(120);
  digitalWrite(LED_PIN, LOW);

  if (ENABLE_BUZZER) {
    noTone(BUZZER_PIN);
  }
}
