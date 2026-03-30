#ifndef ALERT_PATTERNS_H
#define ALERT_PATTERNS_H

// Emergency Alert Patterns Configuration
// =====================================
// This header defines LED and buzzer patterns for each emergency type

struct AlertPattern {
  int ledRed;      // 0 = off, 1 = on, 2 = blink
  int ledYellow;   // 0 = off, 1 = on, 2 = blink
  int ledGreen;    // 0 = off, 1 = on, 2 = blink
  int beepFreq;    // Frequency in Hz (0 = no sound)
  int beepDuration; // Duration in ms
  int beepCount;   // Number of beeps
  unsigned long interval; // Blink interval in ms
};

const AlertPattern PATTERNS[] = {
  // EMERGENCY_NONE - Normal operation
  {
    0, 0, 2,    // Green LED slow pulse
    0, 0, 0,    // No sound
    2000        // 2 second interval
  },
  
  // EMERGENCY_FIRE - Rapid red alert
  {
    2, 1, 0,    // Red blinking, Yellow steady
    2000, 100, 3, // High pitch triple beep
    600         // Fast blink
  },
  
  // EMERGENCY_SMOKE - Medium orange alert
  {
    0, 2, 0,    // Yellow blinking
    1500, 200, 2, // Medium pitch double beep
    800         // Medium blink
  },
  
  // EMERGENCY_GAS - Critical rapid yellow
  {
    2, 2, 0,    // Red and Yellow alternating blink
    2500, 150, 5, // High pitch rapid beeps
    400         // Very fast blink
  },
  
  // EMERGENCY_BLOCKAGE - Blue steady
  {
    0, 1, 0,    // Yellow steady
    1000, 400, 1, // Low single beep
    1000        // Slow blink
  },
  
  // EMERGENCY_CROWD - Purple warning (red+blue)
  {
    2, 0, 0,    // Red blinking
    1800, 150, 2, // Medium double beep
    700         // Medium blink
  }
};

const char* EMERGENCY_NAMES[] = {
  "NONE",
  "FIRE",
  "SMOKE",
  "GAS",
  "BLOCKAGE",
  "CROWD"
};

const char* EMERGENCY_DESCRIPTIONS[] = {
  "System Normal - No Active Emergency",
  "FIRE DETECTED - Evacuate Immediately",
  "SMOKE DETECTED - Stay Low, Evacuate",
  "GAS LEAK - Evacuate, Do Not Use Elevator",
  "BLOCKAGE DETECTED - Use Alternate Route",
  "CROWD CONGESTION - Avoid Area"
};

#endif
