#!/usr/bin/env python3
"""
mock_motec.py — MoTeC CAN Simulator
===================================
Generates fake MoTeC M150 standard output (0x640, 0x648, 0x650, 0x660)
and C125 lap data (0x700) on a SocketCAN interface.
"""

import argparse
import sys
import time
import math

try:
    import can
except ImportError:
    print("[ERROR] 'python-can' not installed. Run: pip install python-can")
    sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description="MoTeC CAN Bus Simulator")
    parser.add_argument("--channel", default="vcan0", help="SocketCAN channel (default: vcan0)")
    args = parser.parse_args()

    channel = args.channel
    print(f"[Sim] Starting MoTeC CAN simulator on '{channel}'...")
    
    try:
        bus = can.interface.Bus(channel=channel, interface="socketcan")
    except Exception as exc:
        print(f"[Sim] Failed to connect to interface: {exc}", file=sys.stderr)
        sys.exit(1)

    t = 0.0
    lap_number = 1
    lap_start_time = time.time()
    
    try:
        while True:
            t += 0.05  # simulation step (20 Hz loop rate)
            
            # --- Message 0x640: Engine speed, throttle, MAP, Coolant ---
            # RPM ranges from 800 (idle) to 9000
            rpm = int(4900 + 4100 * math.sin(t * 0.5)) 
            tps = int((math.sin(t * 0.3) + 1.0) * 50.0 * 10)  # TPS in 0.1% scale (0 to 1000)
            map_val = int((100 + 50 * math.sin(t * 0.7)) * 10)  # kPa in 0.1 scale (500 to 1500)
            ect = int((85 + 2 * math.sin(t * 0.02)) * 10)  # °C in 0.1 scale
            
            # Packs values as UInt16/Int16 LE (Intel byte order)
            data_640 = bytearray()
            data_640.extend(rpm.to_bytes(2, byteorder='little', signed=False))
            data_640.extend(tps.to_bytes(2, byteorder='little', signed=True))
            data_640.extend(map_val.to_bytes(2, byteorder='little', signed=True))
            data_640.extend(ect.to_bytes(2, byteorder='little', signed=True))
            
            # --- Message 0x648: Oil Pres, Oil Temp, IAT, Fuel Pres ---
            oil_pres = int((350 + 100 * math.sin(t * 0.4)) * 10)  # kPa in 0.1 scale
            oil_temp = int((95 + 1 * math.sin(t * 0.01)) * 10)   # °C in 0.1 scale
            iat = int((35 + 2 * math.cos(t * 0.1)) * 10)        # °C in 0.1 scale
            fuel_pres = int((400 + 10 * math.sin(t * 0.05)) * 10) # kPa in 0.1 scale
            
            data_648 = bytearray()
            data_648.extend(oil_pres.to_bytes(2, byteorder='little', signed=True))
            data_648.extend(oil_temp.to_bytes(2, byteorder='little', signed=True))
            data_648.extend(iat.to_bytes(2, byteorder='little', signed=True))
            data_648.extend(fuel_pres.to_bytes(2, byteorder='little', signed=True))

            # --- Message 0x650: Lambda 1, Lambda 2, Fuel Temp, EGT ---
            lambda_1 = int((0.95 + 0.05 * math.sin(t * 0.9)) * 1000)  # La in 0.001 scale
            lambda_2 = int((0.96 + 0.04 * math.cos(t * 0.9)) * 1000)  # La in 0.001 scale
            fuel_temp = int((30 + 1 * math.sin(t * 0.01)) * 10)      # °C in 0.1 scale
            egt = int((750 + 50 * math.sin(t * 0.3)) * 10)           # °C in 0.1 scale

            data_650 = bytearray()
            data_650.extend(lambda_1.to_bytes(2, byteorder='little', signed=False))
            data_650.extend(lambda_2.to_bytes(2, byteorder='little', signed=False))
            data_650.extend(fuel_temp.to_bytes(2, byteorder='little', signed=True))
            data_650.extend(egt.to_bytes(2, byteorder='little', signed=True))

            # --- Message 0x660: Gear, Battery, Speed, Ign Advance ---
            # gear position from -1 (reverse) to 6
            gear = int(3 + 3 * math.sin(t * 0.1))
            batt = int((13.8 + 0.4 * math.sin(t * 0.1)) * 100)       # V in 0.01 scale
            speed = int((120 + 80 * math.sin(t * 0.2)) * 10)         # km/h in 0.1 scale
            ign = int((25 + 5 * math.sin(t * 0.5)) * 10)             # degrees in 0.1 scale

            data_660 = bytearray()
            data_660.extend(gear.to_bytes(2, byteorder='little', signed=True))
            data_660.extend(batt.to_bytes(2, byteorder='little', signed=False))
            data_660.extend(speed.to_bytes(2, byteorder='little', signed=False))
            data_660.extend(ign.to_bytes(2, byteorder='little', signed=True))

            # --- Message 0x700: C125 Lap Data ---
            now = time.time()
            lap_time = int((now - lap_start_time) * 1000) # milliseconds
            
            # Simulate lap completion every 60 seconds
            if lap_time >= 60000:
                lap_number += 1
                lap_start_time = now
                lap_time = 0
                print(f"[Sim] New Lap: {lap_number}")

            btn1 = 1 if math.sin(t) > 0.8 else 0
            btn2 = 1 if math.cos(t) > 0.8 else 0

            data_700 = bytearray()
            data_700.extend(lap_number.to_bytes(2, byteorder='little', signed=False))
            data_700.extend(lap_time.to_bytes(4, byteorder='little', signed=False))
            data_700.append(btn1)
            data_700.append(btn2)

            # Send Messages
            bus.send(can.Message(arbitration_id=0x640, data=data_640, is_extended_id=False))
            bus.send(can.Message(arbitration_id=0x648, data=data_648, is_extended_id=False))
            bus.send(can.Message(arbitration_id=0x650, data=data_650, is_extended_id=False))
            bus.send(can.Message(arbitration_id=0x660, data=data_660, is_extended_id=False))
            bus.send(can.Message(arbitration_id=0x700, data=data_700, is_extended_id=False))

            time.sleep(0.05)  # 20 Hz publish frequency

    except KeyboardInterrupt:
        print("\n[Sim] Stopping simulator...")
    finally:
        bus.shutdown()
        print("[Sim] Done.")

if __name__ == "__main__":
    main()
