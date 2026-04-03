# COMPLETE IoT PROJECT BUILD GUIDE
## Smart Emergency Evacuation System with ESP32

---

# PART 1: SHOPPING LIST

## 1.1 Electronics Components

| # | Component Name | Quantity | Purpose | Where to Buy | Approx Cost |
|---|----------------|----------|---------|--------------|-------------|
| 1 | ESP32 DevKit v1 | 1 | Main microcontroller with WiFi | Amazon, AliExpress, local electronics store | $8-12 |
| 2 | Half-size Breadboard | 1 | Prototyping board for connections | Same as above | $3-5 |
| 3 | Tactile Push Button (6x6x5mm) | 30 | Emergency input buttons | Pack of 50 (with extras) | $3-4 |
| 4 | Jumper Wires (Male-to-Male) | 1 pack (40+ wires) | Making connections | Pack of 120 | $4-6 |
| 5 | Jumper Wires (Male-to-Female) | 1 pack (20 wires) | Extended connections | Pack of 40 | $3-4 |
| 6 | Resistor 220Ω (1/4 Watt) | 3 | Current limiting for LEDs | Pack of 100 | $1-2 |
| 7 | LED - Red (5mm) | 1 | Status indicator (error) | Pack of 50 | $1 |
| 8 | LED - Yellow (5mm) | 1 | Status indicator (processing) | Pack of 50 | $1 |
| 9 | LED - Green (5mm) | 1 | Status indicator (success) | Pack of 50 | $1 |
| 10 | Micro USB Cable | 1 | Power and programming | Old phone charger | $2-3 |
| 11 | (Optional) Buzzer 5V | 1 | Audio alert | Single piece | $1-2 |

### Shopping List Summary

```
REQUIRED (Minimum):
- ESP32 DevKit v1 × 1
- Half-size Breadboard × 1
- Tactile Push Buttons × 30
- Jumper Wires (Male-to-Male) × 1 pack
- 220Ω Resistors × 3
- Red LED × 1
- Yellow LED × 1
- Green LED × 1
- Micro USB Cable × 1

OPTIONAL:
- Jumper Wires (Male-to-Female) × 1 pack
- Buzzer 5V × 1

TOTAL ESTIMATED COST: $25-35
```

---

# PART 2: TOOLS REQUIRED

| # | Tool Name | Purpose | Where to Get |
|---|-----------|---------|--------------|
| 1 | Computer (Windows/Mac/Linux) | Programming ESP32 | Your existing computer |
| 2 | Arduino IDE | Write and upload code to ESP32 | Download from arduino.cc |
| 3 | Internet Browser | Test the web dashboard | Chrome, Firefox, Edge |
| 4 | Wire Cutter/Stripper | Cut and strip wires | Hardware store ($5-10) |
| 5 | Multimeter | Test connections (optional) | Hardware store ($10-20) |

### Software to Install (FREE)

1. **Arduino IDE** - [arduino.cc/en/software](https://www.arduino.cc/en/software)
2. **GitHub Account** - [github.com](https://github.com) (free)
3. **Render Account** - [render.com](https://render.com) (free)

---

# PART 3: COMPLETE STEP-BY-STEP PROCEDURE

---

## STEP 1: Install Arduino IDE

### What: Download and install the software to program ESP32

### Why: Arduino IDE is the tool we'll use to write and upload code to the ESP32 microcontroller

### How:

**1.1 Download Arduino IDE**
- Go to: [arduino.cc/en/software](https://www.arduino.cc/en/software)
- Click **"Windows Win 10 and newer"** (or Mac/Linux version)
- Save the file to your Downloads folder

**1.2 Install Arduino IDE**
- Double-click the downloaded file
- Click **"I Agree"**
- Click **"Install"** (keep default location)
- Click **"Install"** when Windows Security asks
- Click **"Complete"** when done
- **DO NOT** click "Launch Arduino IDE" yet

**1.3 Install ESP32 Board Support**
- Open Arduino IDE
- Go to **File → Preferences**
- Look for **"Additional Board Manager URLs"** field
- Paste this URL exactly:
  ```
  https://raw.githubusercontent.com/espressif/arduino-esp32/gh-pages/package_esp32_index.json
  ```
- Click **OK**

**1.4 Install ESP32 Platform**
- Go to **Tools → Board → Board Manager**
- Wait for download to complete (bottom left shows progress)
- In the search box, type: `esp32`
- Find **"esp32 by Espressif Systems"**
- Click on it
- Click **"Install"** (version 2.0.14 or latest)
- Wait for installation (may take 5-10 minutes)
- Click **"Close"**

**1.5 Verify Installation**
- Go to **Tools → Board**
- Scroll down and find **"ESP32 Arduino"**
- Click on it
- Select **"ESP32 Dev Module"**

### Verification:
- Go to **Tools → Board → ESP32 Arduino → ESP32 Dev Module**
- If you see this option, ESP32 is installed correctly!

---

## STEP 2: Prepare Your Code Files

### What: Organize and configure your project code

### Why: We need to update WiFi credentials and API URL before uploading

### How:

**2.1 Locate Your Project Files**
- Your project should be at: `C:\Users\Moham\Downloads\project4`
- Open the folder and find:
  - `esp32/firmware/esp32_emergency_controller/`

**2.2 Open config.h for Editing**
- Go to: `esp32/firmware/esp32_emergency_controller/config.h`
- Right-click → **Open with → Notepad** (or any text editor)

**2.3 Edit WiFi Settings**
Find these lines and update:

```cpp
#define WIFI_SSID "YourWiFiName"
#define WIFI_PASSWORD "YourWiFiPassword"
```

Change `YourWiFiName` to your actual WiFi name (case sensitive!)
Change `YourWiFiPassword` to your WiFi password

**Example (after editing):**
```cpp
#define WIFI_SSID "MyHomeWiFi"
#define WIFI_PASSWORD "MyPassword123"
```

**2.4 Edit API URL** (We'll do this AFTER deploying backend in Step 6)
- For now, leave it as: `http://localhost:5000`
- We'll change it to your deployed URL later

**2.5 Save the file**
- Press **Ctrl + S** to save
- Close the file

### Verification:
- Open config.h again and confirm your WiFi name and password are saved correctly

---

## STEP 3: Wire the Breadboard

### What: Connect all 30 buttons in a 5×6 matrix pattern

### Why: The button matrix allows 30 buttons using only 11 GPIO pins (5 rows + 6 columns)

### How:

**IMPORTANT: Work on a clean, flat surface. Keep ESP32 disconnected from USB until wiring is complete.**

**3.1 Place ESP32 on Breadboard**
- Place ESP32 DevKit at the TOP of your breadboard
- Align it so the pins straddle the center groove
- The USB connector should face OUTWARD (away from you)

**3.2 Identify Button Legs**
Before placing buttons, identify which legs connect:
- Take one button
- Look at it from the side with legs facing you
- The two legs on the LEFT are connected together
- The two legs on the RIGHT are connected together
- When you press the button, ALL FOUR legs connect

**3.3 Place Row 0 (Buttons 0-5)**
- Place 6 buttons in the first row
- Button 0 should be leftmost
- Button 5 should be rightmost
- Leave one row of breadboard holes between ESP32 and buttons

**3.4 Place Row 1 (Buttons 6-11)**
- Place 6 buttons below Row 0
- Align them directly under buttons 0-5

**3.5 Place Row 2 (Buttons 12-17)**
- Place 6 buttons below Row 1

**3.6 Place Row 3 (Buttons 18-23)**
- Place 6 buttons below Row 2

**3.7 Place Row 4 (Buttons 24-29)**
- Place 6 buttons below Row 3

### Your button layout should look like this:

```
        Col0   Col1   Col2   Col3   Col4   Col5
         │      │      │      │      │      │
    ─────┴──────┴──────┴──────┴──────┴──────┴────── GPIO 4 (Row 0)
     Btn0  Btn1  Btn2  Btn3  Btn4  Btn5
    ─────┴──────┴──────┴──────┴──────┴──────┴────── GPIO 5 (Row 1)
     Btn6  Btn7  Btn8  Btn9  Btn10 Btn11
    ─────┴──────┴──────┴──────┴──────┴──────┴────── GPIO 6 (Row 2)
    Btn12 Btn13 Btn14 Btn15 Btn16 Btn17
    ─────┴──────┴──────┴──────┴──────┴──────┴────── GPIO 7 (Row 3)
    Btn18 Btn19 Btn20 Btn21 Btn22 Btn23
    ─────┴──────┴──────┴──────┴──────┴──────┴────── GPIO 8 (Row 4)
    Btn24 Btn25 Btn26 Btn27 Btn28 Btn29
```

---

## STEP 4: Connect Row Wires (GPIO 4-8)

### What: Wire each row of buttons to a GPIO pin

### Why: Each row needs one wire from ESP32 to detect button presses

### How:

**4.1 Wire Row 0 to GPIO 4**
- Take ONE jumper wire (use ORANGE if possible)
- Connect one end to ESP32 **GPIO 4** pin
- Connect other end to the breadboard row where ALL Row 0 buttons have their left legs connected
- **Tip:** Use the breadboard's vertical rails - connect a wire from GPIO 4 to the rail, then connect each button's left leg to that rail

**4.2 Wire Row 1 to GPIO 5**
- Take another jumper wire
- Connect one end to ESP32 **GPIO 5** pin
- Connect other end to the breadboard row where ALL Row 1 buttons have their left legs connected

**4.3 Wire Row 2 to GPIO 6**
- Connect ESP32 **GPIO 6** to ALL Row 2 buttons' left legs

**4.4 Wire Row 3 to GPIO 7**
- Connect ESP32 **GPIO 7** to ALL Row 3 buttons' left legs

**4.5 Wire Row 4 to GPIO 8**
- Connect ESP32 **GPIO 8** to ALL Row 4 buttons' left legs

### Visual Reference:
```
GPIO 4 ─────┬────┬────┬────┬────┬────┬────┐
            │    │    │    │    │    │    │
          Btn0 Btn1 Btn2 Btn3 Btn4 Btn5 (Row 0)
```

---

## STEP 5: Connect Column Wires (GPIO 9-14)

### What: Wire each column of buttons to a GPIO pin

### Why: Each column needs one wire from ESP32 to complete the button detection circuit

### How:

**5.1 Wire Column 0 to GPIO 9**
- Take ONE jumper wire (use BLUE if possible)
- Connect one end to ESP32 **GPIO 9** pin
- Connect other end to ONE leg of buttons: 0, 6, 12, 18, 24
- Use a vertical rail for easier connection

**5.2 Wire Column 1 to GPIO 10**
- Connect ESP32 **GPIO 10** to buttons: 1, 7, 13, 19, 25

**5.3 Wire Column 2 to GPIO 11**
- Connect ESP32 **GPIO 11** to buttons: 2, 8, 14, 20, 26

**5.4 Wire Column 3 to GPIO 12**
- Connect ESP32 **GPIO 12** to buttons: 3, 9, 15, 21, 27

**5.5 Wire Column 4 to GPIO 13**
- Connect ESP32 **GPIO 13** to buttons: 4, 10, 16, 22, 28

**5.6 Wire Column 5 to GPIO 14**
- Connect ESP32 **GPIO 14** to buttons: 5, 11, 17, 23, 29

---

## STEP 6: Connect Common Ground

### What: Connect all buttons to ESP32 ground (GND)

### Why: Buttons need a common ground reference to work properly

### How:

**6.1 Identify GND Pins on ESP32**
- Look for **GND** pins near the GPIO pins
- ESP32 has multiple GND pins - you can use any one

**6.2 Wire to Ground Rail**
- Take a jumper wire (use BLACK)
- Connect one end to any ESP32 **GND** pin
- Connect other end to the breadboard's **negative (-) rail** (usually blue line)

**6.3 Connect All Button Legs to Ground**
- Connect the remaining legs of ALL 30 buttons to the **negative (-) rail**
- This creates a common ground for all buttons

### Visual:
```
ESP32 GND ──→ Negative Rail (Blue) ──→ All Button Remaining Legs
```

---

## STEP 7: Wire the Status LEDs

### What: Connect 3 LEDs to show system status

### Why: LEDs provide visual feedback (success, processing, error)

### How:

**7.1 Place Resistors**
- Place 3 resistors on the breadboard near the ESP32
- Position them so one end is near GPIO 15, 16, 17

**7.2 Place LEDs**
- Place Red LED near resistor for GPIO 15
- Place Yellow LED near resistor for GPIO 16
- Place Green LED near resistor for GPIO 17
- **IMPORTANT:** Identify LED polarity
  - Long leg = Anode (+)
  - Short leg = Cathode (-)

**7.3 Wire Red LED (GPIO 15)**
- Connect ESP32 **GPIO 15** to one leg of **220Ω resistor**
- Connect other leg of resistor to **long leg (anode)** of Red LED
- Connect **short leg (cathode)** of Red LED to **GND**

**7.4 Wire Yellow LED (GPIO 16)**
- Connect ESP32 **GPIO 16** to one leg of **220Ω resistor**
- Connect other leg of resistor to **long leg** of Yellow LED
- Connect **short leg** of Yellow LED to **GND**

**7.5 Wire Green LED (GPIO 17)**
- Connect ESP32 **GPIO 17** to one leg of **220Ω resistor**
- Connect other leg of resistor to **long leg** of Green LED
- Connect **short leg** of Green LED to **GND**

### Circuit Diagram:
```
GPIO 15 ──[220Ω]──►| RED LED |─── GND
GPIO 16 ──[220Ω]──►| YEL LED |─── GND
GPIO 17 ──[220Ω]──►| GRN LED |─── GND
```

---

## STEP 8: Upload Firmware to ESP32

### What: Transfer your code to the ESP32 microcontroller

### Why: The ESP32 needs code to know what to do with all those buttons and LEDs

### How:

**8.1 Connect ESP32 to Computer**
- Plug the Micro USB cable into ESP32
- Plug other end into your computer's USB port
- Wait for Windows to install drivers (automatic)

**8.2 Open the Project in Arduino IDE**
- Open Arduino IDE
- Go to **File → Open**
- Navigate to: `C:\Users\Moham\Downloads\project4\esp32\firmware\esp32_emergency_controller\`
- Open: `esp32_emergency_controller.ino`
- The file should open with multiple tabs

**8.3 Select the Correct Board**
- Go to **Tools → Board → ESP32 Arduino**
- Select: **ESP32 Dev Module**

**8.4 Select the Correct Port**
- Go to **Tools → Port**
- Select the COM port with **(ESP32)** or **(USB-SERIAL)**
- If no COM port appears:
  - Try a different USB cable (must be data cable, not charge-only)
  - Try a different USB port
  - Install CH340 driver (search online for "ESP32 CH340 driver")

**8.5 Configure Upload Settings**
- Go to **Tools** and verify:
  - **Board:** "ESP32 Dev Module"
  - **Upload Speed:** "115200"
  - **Partition Scheme:** "Default 4MB with spiffs"
  - **Port:** (Your COM port)

**8.6 Upload the Code**
- Press **Ctrl + U** (or click Upload button →)
- Wait for compilation (1-2 minutes first time)
- Watch the bottom of Arduino IDE for progress:
  ```
  Sketch uses 123456 bytes (XX%) of program storage space...
  ```
- When upload starts, you'll see:
  ```
  Hard resetting via RTS pin...
  ```
- When complete, you'll see:
  ```
  Done uploading.
  ```

### Verification:
- Open **Tools → Serial Monitor**
- Set baud rate to **115200**
- Press the ESP32 **EN** button (on the board)
- You should see:
  ```
  ESP32 Emergency Controller
  WiFi connecting to: YourWiFiName
  WiFi connected!
  ESP32 ready and listening for button presses...
  ```

---

## STEP 9: Deploy Backend to Internet

### What: Put your Flask backend on a server so ESP32 can send data

### Why: ESP32 needs to send emergency data to a web server that everyone can access

### How:

**9.1 Push Code to GitHub**
- Go to [github.com](https://github.com)
- Click **"+"** (top right) → **"New repository"**
- Name it: `smart-evacuation`
- Select: **Public** (free hosting)
- Click **"Create repository"**
- Follow the instructions to push your code:
  ```bash
  git init
  git add .
  git commit -m "Smart Evacuation System"
  git branch -M main
  git remote add origin https://github.com/YOURUSERNAME/smart-evacuation.git
  git push -u origin main
  ```
- Refresh GitHub page - your code is now online!

**9.2 Deploy to Render**
- Go to [render.com](https://render.com)
- Click **"Sign Up"**
- Choose **"GitHub"** to sign up
- Authorize Render to access your GitHub

**9.3 Create Web Service**
- Click **"New +"** (top left)
- Select **"Web Service"**
- Under "Connect a GitHub Repository":
  - Find and select your `smart-evacuation` repo
  - Click **"Connect"**

**9.4 Configure the Service**
Fill in these settings:

| Setting | Value |
|---------|-------|
| **Name** | `smart-evacuation` (or any name you want) |
| **Region** | Singapore (or closest to you) |
| **Branch** | `main` |
| **Root Directory** | `backend` |
| **Runtime** | `Python 3` |
| **Build Command** | `pip install -r requirements.txt` |
| **Start Command** | `gunicorn app:app -b 0.0.0.0:10000` |

**9.5 Add Environment Variable**
- Scroll to "Environment"
- Click **"Add Environment Variable"**
- Add:
  - Key: `PORT`
  - Value: `10000`

**9.6 Create the Service**
- Click **"Create Web Service"**
- Wait 2-3 minutes for deployment
- You'll see logs scrolling by
- When complete, you'll see green "Live" status

**9.7 Note Your URL**
- Your URL will be shown at the top
- Example: `https://smart-evacuation.onrender.com`
- **Save this URL!**

### Verification:
- Open your URL in a browser
- You should see your Smart Evacuation dashboard!

---

## STEP 10: Configure ESP32 with Your URL

### What: Update ESP32 code with your deployed backend URL

### Why: ESP32 needs to know WHERE to send emergency data

### How:

**10.1 Update config.h**
- Go back to Arduino IDE
- Open: `esp32/firmware/esp32_emergency_controller/config.h`
- Find this line:
  ```cpp
  #define API_HOST "http://localhost:5000"
  ```
- Change it to your Render URL (remove http:// and trailing slash):
  ```cpp
  #define API_HOST "https://smart-evacuation.onrender.com"
  ```

**10.2 Save and Re-upload**
- Save the file: **Ctrl + S**
- Upload again: **Ctrl + U**
- Wait for upload to complete

**10.3 Test the Connection**
- Open **Tools → Serial Monitor** (115200 baud)
- Press ESP32 **EN** button
- You should see:
  ```
  ESP32 Emergency Controller
  WiFi connecting to: YourWiFiName
  WiFi connected!
  ESP32 ready!
  ```

**10.4 Test a Button Press**
- Press any button on your matrix
- Check Serial Monitor:
  ```
  Button 0 pressed
  Type: FIRE
  Sending to API...
  Response: 200
  ```
- Open your Render URL in a browser
- You should see the emergency appear on the map!

---

# PART 4: TESTING & TROUBLESHOOTING

## Testing Checklist

### Test 1: WiFi Connection
- [ ] ESP32 connects to WiFi
- [ ] Serial monitor shows "WiFi connected"

### Test 2: Button Matrix
- [ ] All 30 buttons register when pressed
- [ ] Serial monitor shows correct button number
- [ ] Pressing multiple buttons works

### Test 3: Status LEDs
- [ ] Red LED lights up (error state)
- [ ] Yellow LED lights up (processing)
- [ ] Green LED lights up (success)

### Test 4: Backend Connection
- [ ] Button press sends data to server
- [ ] Serial monitor shows "Response: 200"
- [ ] Dashboard updates in browser

### Test 5: Evacuation Route
- [ ] Select a start room
- [ ] Click "RUN EVACUATION"
- [ ] Route displays on map
- [ ] Distance is accurate

## Common Problems & Solutions

### Problem: "WiFi connection failed"
**Solution:**
1. Check WiFi name and password in config.h
2. Make sure WiFi is 2.4GHz (not 5GHz)
3. Move ESP32 closer to router
4. Restart ESP32 and try again

### Problem: "COM port not showing"
**Solution:**
1. Try different USB cable (must be data cable)
2. Try different USB port on computer
3. Install CH340 driver (search "ESP32 CH340 driver download")
4. Unplug and replug ESP32

### Problem: "Button not responding"
**Solution:**
1. Check the row wire connection
2. Check the column wire connection
3. Make sure button is properly seated
4. Check for loose wires

### Problem: "API upload failed (404)"
**Solution:**
1. Check config.h has correct URL
2. Make sure Render service is "Live" (not sleeping)
3. Re-upload code to ESP32
4. Check Render logs for errors

### Problem: "LED not lighting"
**Solution:**
1. Check LED polarity (long leg toward resistor)
2. Make sure resistor is connected (not bypassed)
3. Test LED separately with 3.3V

---

# PART 5: QUICK REFERENCE

## Pin Assignment Summary

| GPIO | Direction | Purpose |
|------|-----------|---------|
| GPIO 4 | OUTPUT | Row 0 (Buttons 0-5) |
| GPIO 5 | OUTPUT | Row 1 (Buttons 6-11) |
| GPIO 6 | OUTPUT | Row 2 (Buttons 12-17) |
| GPIO 7 | OUTPUT | Row 3 (Buttons 18-23) |
| GPIO 8 | OUTPUT | Row 4 (Buttons 24-29) |
| GPIO 9 | INPUT_PULLUP | Column 0 (Buttons 0,6,12,18,24) |
| GPIO 10 | INPUT_PULLUP | Column 1 (Buttons 1,7,13,19,25) |
| GPIO 11 | INPUT_PULLUP | Column 2 (Buttons 2,8,14,20,26) |
| GPIO 12 | INPUT_PULLUP | Column 3 (Buttons 3,9,15,21,27) |
| GPIO 13 | INPUT_PULLUP | Column 4 (Buttons 4,10,16,22,28) |
| GPIO 14 | INPUT_PULLUP | Column 5 (Buttons 5,11,17,23,29) |
| GPIO 15 | OUTPUT | Red LED |
| GPIO 16 | OUTPUT | Yellow LED |
| GPIO 17 | OUTPUT | Green LED |
| GND | POWER | Common ground |

## Button Number Map

```
     C0   C1   C2   C3   C4   C5
R0 │  0 │  1 │  2 │  3 │  4 │  5 │
R1 │  6 │  7 │  8 │  9 │ 10 │ 11 │
R2 │ 12 │ 13 │ 14 │ 15 │ 16 │ 17 │
R3 │ 18 │ 19 │ 20 │ 21 │ 22 │ 23 │
R4 │ 24 │ 25 │ 26 │ 27 │ 28 │ 29 │
```

## Important URLs

| Service | URL |
|---------|-----|
| Arduino IDE Download | arduino.cc/en/software |
| ESP32 Board Manager | (paste in Preferences) |
| GitHub | github.com |
| Render Deployment | render.com |
| Your Backend | (your Render URL) |

---

# PART 6: NEXT STEPS (After Building)

## Congratulations! Your System is Complete!

Now you can:

1. **Use the IoT Control Panel** (browser-based, no ESP32 needed)
   - Go to: `YOUR_URL/iot_control_panel.html`

2. **Use with Real ESP32** (hardware version)
   - Press buttons on the matrix
   - Watch hazards appear on dashboard
   - Run evacuation routes

3. **Present for Project/Viva**
   - Show the working hardware
   - Demonstrate button → WiFi → Dashboard flow
   - Explain ACO algorithm for pathfinding

---

## Questions?

If you get stuck:
1. Check the Troubleshooting section above
2. Look at Serial Monitor output for clues
3. Check Render deployment logs
4. Ask for help with specific error messages

**Good luck with your project!**
