"""
iot_simulator.py - IoT Sensor Simulator for Smart Evacuation System
====================================================================
Simulates emergency sensor triggers and communicates with Flask backend.
Can run standalone or alongside the main application.

Usage:
    python iot_simulator.py              # Interactive mode
    python iot_simulator.py --auto       # Auto demo mode
    python iot_simulator.py --fire 5     # Trigger sensor_5 as FIRE
    python iot_simulator.py --clear      # Clear all emergencies

Author: Smart Evacuation System
Version: 1.0
"""

import requests
import time
import random
import argparse
import sys
from datetime import datetime
from typing import Optional, List, Dict

# Configuration
API_HOST = "http://localhost:5000"
TOTAL_SENSORS = 30

EMERGENCY_TYPES = ["FIRE", "SMOKE", "GAS", "BLOCKAGE", "CROWD"]

SENSOR_NAMES = [
    "C1A-North", "C1B-North", "C1C-North", "C1D-North", "C2A-Left", "C2B-Left",
    "C3A-Right", "C3B-Right", "C3C-Right", "C3D-Right", "C4A-NCorr", "C4B-ECorr",
    "C5A-CCorr", "C5B-CCorr", "C6A-SCorr", "C6B-SCorr", "CJ-NW", "CJ-NC",
    "CJ-NE", "CJ-MW", "CJ-MC", "CJ-ME", "CJ-SW", "CJ-SC",
    "CJ-SE", "C7A-NWSt", "C7B-NESt", "C7C-ESLobby", "STORED", "RESERVED"
]

SCENARIOS = {
    "demo": {"name": "Demo Mode", "sensors": [0, 4, 8, 12, 16], "types": ["FIRE", "SMOKE", "GAS", "BLOCKAGE", "CROWD"]},
    "north_fire": {"name": "North Wing Fire", "sensors": [4, 5, 12], "types": ["FIRE"]},
    "south_fire": {"name": "South Wing Fire", "sensors": [6, 7, 16, 17], "types": ["FIRE"]},
    "cascade": {"name": "Fire Cascade", "sensors": [0, 1, 4, 2, 5, 8], "types": ["FIRE"]},
    "smoke": {"name": "Smoke Spread", "sensors": [1, 2, 5, 6, 9], "types": ["SMOKE"]},
    "gas": {"name": "Gas Leak", "sensors": [13, 15, 19], "types": ["GAS"]},
    "blockage": {"name": "Route Block", "sensors": [12, 13, 18, 19], "types": ["BLOCKAGE"]},
    "full": {"name": "Full Emergency", "sensors": [0, 8, 16, 24], "types": ["FIRE", "FIRE", "SMOKE", "GAS"]},
}


class IoTSimulator:
    """IoT Sensor Simulator"""
    
    def __init__(self, api_host: str = API_HOST):
        self.api_host = api_host
        self.active_sensors: set = set()
        self.stats = {"triggers": 0, "successful": 0, "failed": 0}
        self.connected = False
        
    def test_connection(self) -> bool:
        """Test connection to Flask backend"""
        try:
            response = requests.get(f"{self.api_host}/api", timeout=3)
            self.connected = response.ok
            return self.connected
        except requests.exceptions.RequestException:
            self.connected = False
            return False
    
    def trigger_sensor(self, sensor_num: int, emergency_type: str = "FIRE") -> bool:
        """Trigger a sensor with specified emergency type"""
        if sensor_num < 0 or sensor_num >= TOTAL_SENSORS:
            print(f"  [ERROR] Invalid sensor number: {sensor_num}")
            return False
            
        sensor_id = f"sensor_{sensor_num}"
        
        try:
            response = requests.post(
                f"{self.api_host}/sensor-update",
                json={"sensor_id": sensor_id, "type": emergency_type},
                timeout=5
            )
            
            self.stats["triggers"] += 1
            
            if response.ok:
                self.active_sensors.add(sensor_num)
                self.stats["successful"] += 1
                sensor_name = SENSOR_NAMES[sensor_num] if sensor_num < len(SENSOR_NAMES) else "Unknown"
                print(f"  [OK] {sensor_id} ({sensor_name}) - {emergency_type}")
                return True
            else:
                self.stats["failed"] += 1
                print(f"  [FAIL] {sensor_id} - HTTP {response.status_code}")
                return False
                
        except requests.exceptions.RequestException as e:
            self.stats["failed"] += 1
            print(f"  [ERROR] {sensor_id} - {e}")
            return False
    
    def clear_sensor(self, sensor_num: int) -> bool:
        """Clear a specific sensor"""
        sensor_id = f"sensor_{sensor_num}"
        
        try:
            response = requests.post(
                f"{self.api_host}/reset-emergencies",
                json={"sensor_id": sensor_id},
                timeout=5
            )
            
            if response.ok:
                self.active_sensors.discard(sensor_num)
                print(f"  [CLEARED] {sensor_id}")
                return True
            return False
            
        except requests.exceptions.RequestException as e:
            print(f"  [ERROR] Failed to clear {sensor_id}: {e}")
            return False
    
    def clear_all(self) -> bool:
        """Clear all active emergencies"""
        try:
            response = requests.post(
                f"{self.api_host}/reset-emergencies",
                json={},
                timeout=5
            )
            
            if response.ok:
                self.active_sensors.clear()
                print("[CLEARED] All emergencies cleared")
                return True
            return False
            
        except requests.exceptions.RequestException as e:
            print(f"[ERROR] Failed to clear emergencies: {e}")
            return False
    
    def get_status(self) -> Optional[Dict]:
        """Get current sensor status from backend"""
        try:
            response = requests.get(f"{self.api_host}/sensor-status", timeout=5)
            if response.ok:
                return response.json()
            return None
        except requests.exceptions.RequestException:
            return None
    
    def run_scenario(self, scenario_name: str, delay: float = 1.5) -> bool:
        """Run a pre-defined scenario"""
        if scenario_name not in SCENARIOS:
            print(f"[ERROR] Unknown scenario: {scenario_name}")
            print(f"Available: {', '.join(SCENARIOS.keys())}")
            return False
        
        scenario = SCENARIOS[scenario_name]
        print(f"\n{'='*50}")
        print(f"SCENARIO: {scenario['name']}")
        print(f"{'='*50}")
        
        for i, sensor_num in enumerate(scenario["sensors"]):
            emergency_type = scenario["types"][i % len(scenario["types"])]
            self.trigger_sensor(sensor_num, emergency_type)
            time.sleep(delay)
        
        print(f"\n[COMPLETE] Scenario '{scenario['name']}' finished")
        return True
    
    def auto_demo(self, duration: int = 60):
        """Run automatic demo with random triggers"""
        print(f"\n{'='*50}")
        print(f"AUTO DEMO MODE - Running for {duration} seconds")
        print(f"{'='*50}")
        
        end_time = time.time() + duration
        trigger_count = 0
        
        while time.time() < end_time:
            sensor_num = random.randint(0, TOTAL_SENSORS - 1)
            emergency_type = random.choice(EMERGENCY_TYPES)
            
            print(f"\n[{datetime.now().strftime('%H:%M:%S')}] Auto-trigger #{trigger_count + 1}")
            self.trigger_sensor(sensor_num, emergency_type)
            
            trigger_count += 1
            
            wait_time = random.uniform(3, 8)
            print(f"  Waiting {wait_time:.1f}s...")
            time.sleep(wait_time)
            
            if random.random() < 0.3 and self.active_sensors:
                clear_sensor = random.choice(list(self.active_sensors))
                print(f"\n[{datetime.now().strftime('%H:%M:%S')}] Auto-clear")
                self.clear_sensor(clear_sensor)
            
            if trigger_count >= 10:
                print("\n[AUTO] Clearing all for fresh start...")
                self.clear_all()
                trigger_count = 0
        
        print(f"\n[COMPLETE] Auto demo finished")
    
    def print_stats(self):
        """Print statistics"""
        print(f"\n{'='*50}")
        print("STATISTICS")
        print(f"{'='*50}")
        print(f"Total Triggers: {self.stats['triggers']}")
        print(f"Successful:     {self.stats['successful']}")
        print(f"Failed:         {self.stats['failed']}")
        if self.stats['triggers'] > 0:
            success_rate = (self.stats['successful'] / self.stats['triggers']) * 100
            print(f"Success Rate:   {success_rate:.1f}%")
        print(f"Active Sensors: {len(self.active_sensors)}")
        if self.active_sensors:
            print(f"Active IDs:     {sorted(self.active_sensors)}")
        print(f"{'='*50}")


def interactive_mode(simulator: IoTSimulator):
    """Interactive command-line mode"""
    print(f"""
{'='*50}
IoT SENSOR SIMULATOR - Interactive Mode
{'='*50}
Commands:
  trigger <sensor_num> [type]  - Trigger a sensor (0-{TOTAL_SENSORS-1})
  clear <sensor_num>           - Clear a specific sensor
  clearall                      - Clear all emergencies
  status                        - Show sensor status
  scenario <name>               - Run a scenario ({', '.join(SCENARIOS.keys())})
  demo                          - Run auto demo (60s)
  stats                         - Show statistics
  test                          - Test connection
  help                          - Show this help
  quit                          - Exit
{'='*50}
""")
    
    while True:
        try:
            cmd = input("\n> ").strip().lower()
            
            if not cmd:
                continue
                
            parts = cmd.split()
            action = parts[0]
            
            if action == "quit" or action == "exit" or action == "q":
                print("Goodbye!")
                break
                
            elif action == "help" or action == "h":
                print("""
Commands:
  trigger <num> [type]  - Trigger sensor (type: FIRE, SMOKE, GAS, BLOCKAGE, CROWD)
  clear <num>           - Clear specific sensor
  clearall              - Clear all
  status                - Get status
  scenario <name>       - Run scenario
  demo                  - Auto demo (60s)
  stats                 - Show stats
  test                  - Test connection
  quit                  - Exit
                """)
                
            elif action == "test" or action == "t":
                if simulator.test_connection():
                    print("[OK] Connected to Flask backend")
                else:
                    print("[ERROR] Cannot connect to Flask backend")
                    print(f"  Make sure backend is running at {simulator.api_host}")
                    
            elif action == "trigger" or action == "trig":
                if len(parts) < 2:
                    print("[ERROR] Usage: trigger <sensor_num> [type]")
                else:
                    try:
                        sensor_num = int(parts[1])
                        emergency_type = parts[2].upper() if len(parts) > 2 else "FIRE"
                        simulator.trigger_sensor(sensor_num, emergency_type)
                    except ValueError:
                        print("[ERROR] Invalid sensor number")
                        
            elif action == "clear":
                if len(parts) < 2:
                    print("[ERROR] Usage: clear <sensor_num>")
                else:
                    try:
                        sensor_num = int(parts[1])
                        simulator.clear_sensor(sensor_num)
                    except ValueError:
                        print("[ERROR] Invalid sensor number")
                        
            elif action == "clearall":
                simulator.clear_all()
                
            elif action == "status" or action == "s":
                status = simulator.get_status()
                if status:
                    print(f"Active Emergencies: {len(status.get('active_emergencies', []))}")
                    for emp in status.get('active_emergencies', []):
                        print(f"  - {emp.get('sensor_id')}: {emp.get('type')}")
                else:
                    print("[ERROR] Failed to get status")
                    
            elif action == "scenario":
                if len(parts) < 2:
                    print(f"[ERROR] Usage: scenario <name>")
                    print(f"Available: {', '.join(SCENARIOS.keys())}")
                else:
                    simulator.run_scenario(parts[1])
                    
            elif action == "demo":
                simulator.auto_demo()
                
            elif action == "stats":
                simulator.print_stats()
                
            else:
                print(f"[ERROR] Unknown command: {action}")
                print("Type 'help' for available commands")
                
        except KeyboardInterrupt:
            print("\n\nInterrupted. Type 'quit' to exit.")
        except Exception as e:
            print(f"[ERROR] {e}")


def main():
    parser = argparse.ArgumentParser(description="IoT Sensor Simulator")
    parser.add_argument("--host", default=API_HOST, help=f"Flask API host (default: {API_HOST})")
    parser.add_argument("--auto", action="store_true", help="Run automatic demo mode")
    parser.add_argument("--fire", type=int, metavar="N", help="Trigger sensor N as FIRE")
    parser.add_argument("--smoke", type=int, metavar="N", help="Trigger sensor N as SMOKE")
    parser.add_argument("--gas", type=int, metavar="N", help="Trigger sensor N as GAS")
    parser.add_argument("--blockage", type=int, metavar="N", help="Trigger sensor N as BLOCKAGE")
    parser.add_argument("--crowd", type=int, metavar="N", help="Trigger sensor N as CROWD")
    parser.add_argument("--clear", action="store_true", help="Clear all emergencies")
    parser.add_argument("--scenario", choices=list(SCENARIOS.keys()), help="Run a specific scenario")
    parser.add_argument("--interactive", "-i", action="store_true", help="Start interactive mode")
    
    args = parser.parse_args()
    
    simulator = IoTSimulator(api_host=args.host)
    
    print(f"\nIoT Sensor Simulator v1.0")
    print(f"Target: {args.host}")
    
    if not simulator.test_connection():
        print(f"\n[WARNING] Cannot connect to Flask backend at {args.host}")
        print("Make sure the backend is running. Simulator will still work in local mode.")
        print()
    else:
        print("[OK] Connected to Flask backend\n")
    
    if args.fire is not None:
        simulator.trigger_sensor(args.fire, "FIRE")
    elif args.smoke is not None:
        simulator.trigger_sensor(args.smoke, "SMOKE")
    elif args.gas is not None:
        simulator.trigger_sensor(args.gas, "GAS")
    elif args.blockage is not None:
        simulator.trigger_sensor(args.blockage, "BLOCKAGE")
    elif args.crowd is not None:
        simulator.trigger_sensor(args.crowd, "CROWD")
    elif args.clear:
        simulator.clear_all()
    elif args.scenario:
        simulator.run_scenario(args.scenario)
    elif args.auto:
        simulator.auto_demo()
    else:
        interactive_mode(simulator)
    
    simulator.print_stats()


if __name__ == "__main__":
    main()
