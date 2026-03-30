#ifndef CONFIG_H
#define CONFIG_H

// Smart Evacuation System - Configuration
// =========================================

// Button Matrix Configuration
#define MATRIX_ROWS 5
#define MATRIX_COLS 6
#define TOTAL_BUTTONS (MATRIX_ROWS * MATRIX_COLS)

// Pin Definitions
#define ROW_PIN_0 2
#define ROW_PIN_1 3
#define ROW_PIN_2 4
#define ROW_PIN_3 5
#define ROW_PIN_4 6

#define COL_PIN_0 7
#define COL_PIN_1 8
#define COL_PIN_2 9
#define COL_PIN_3 10
#define COL_PIN_4 11
#define COL_PIN_5 12

// Status LED Pins
#define LED_GREEN A1
#define LED_YELLOW A2
#define LED_RED A3

// Buzzer Pin
#define BUZZER_PIN A0

// LCD I2C Address
#define LCD_ADDRESS 0x27
#define LCD_COLS 16
#define LCD_ROWS 2

// Timing Parameters (in milliseconds)
#define DEBOUNCE_DELAY 60
#define REPEAT_BLOCK_DELAY 1500
#define LCD_UPDATE_INTERVAL 500
#define LED_BLINK_INTERVAL 200
#define AUTO_CLEAR_TIMEOUT 60000
#define SERIAL_TIMEOUT 1000

// Serial Communication
#define SERIAL_BAUD 9600
#define SERIAL_DELIMITER '\n'

// Sensor to Corridor Mapping
const char* SENSOR_CORRIDOR_MAP[] = {
  "C1A",  // sensor_0
  "C1B",  // sensor_1
  "C1C",  // sensor_2
  "C1D",  // sensor_3
  "C2A",  // sensor_4
  "C2B",  // sensor_5
  "C2C",  // sensor_6
  "C2D",  // sensor_7
  "C3A",  // sensor_8
  "C3B",  // sensor_9
  "C3C",  // sensor_10
  "C3D",  // sensor_11
  "C4A",  // sensor_12
  "C4B",  // sensor_13
  "C5A",  // sensor_14
  "C5B",  // sensor_15
  "C6A",  // sensor_16
  "C6B",  // sensor_17
  "CJ_NW", // sensor_18
  "CJ_NC", // sensor_19
  "CJ_NE", // sensor_20
  "CJ_MW", // sensor_21
  "CJ_MC", // sensor_22
  "CJ_ME", // sensor_23
  "CJ_SW", // sensor_24
  "CJ_SC", // sensor_25
  "CJ_SE", // sensor_26
  "C7A",  // sensor_27
  "C7B",  // sensor_28
  "C7C"   // sensor_29
};

#endif
