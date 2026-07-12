#!/usr/bin/env python3
"""
can_sniffer.py — MoTeC CAN Sniffer Tool
=======================================
Analyzes and displays incoming CAN frames, their message frequency, 
data length, and updates live. Helps discover IDs without a DBC.
"""

import argparse
import sys
import time
from collections import defaultdict

try:
    import can
except ImportError:
    print("[ERROR] 'python-can' not installed. Run: pip install python-can")
    sys.exit(1)

def run_sniffer(channel: str, duration: float):
    print("=" * 65)
    print(f" MoTeC CAN Sniffer — Listening on '{channel}'")
    print(f" Duration: {duration if duration > 0 else 'Infinite'} seconds")
    print("=" * 65)
    print(f"{'CAN ID':<10} | {'DLC':<4} | {'Count':<7} | {'Hz':<6} | {'Last Data (Hex)':<25}")
    print("-" * 65)

    try:
        if channel.startswith("vcan"):
            bus = can.interface.Bus(channel=channel, interface="socketcan")
        else:
            bus = can.interface.Bus(channel=channel, interface="socketcan", bitrate=1000000)
    except Exception as exc:
        print(f"[ERROR] Failed to open bus '{channel}': {exc}", file=sys.stderr)
        sys.exit(1)

    start_time = time.time()
    msg_counts = defaultdict(int)
    msg_last_seen = {}
    msg_last_data = {}

    try:
        while True:
            elapsed = time.time() - start_time
            if duration > 0 and elapsed >= duration:
                break

            msg = bus.recv(timeout=0.1)
            if msg is None:
                continue

            msg_id = msg.arbitration_id
            now = time.time()
            
            msg_counts[msg_id] += 1
            msg_last_seen[msg_id] = now
            msg_last_data[msg_id] = msg.data

            # Print updates every 0.5s or on key metrics
            if sum(msg_counts.values()) % 20 == 0:
                sys.stdout.write("\033[H\033[J") # clear terminal screen
                print("=" * 65)
                print(f" MoTeC CAN Sniffer — Live Status (Elapsed: {elapsed:.1f} s)")
                print("=" * 65)
                print(f"{'CAN ID':<10} | {'DLC':<4} | {'Count':<7} | {'Hz':<6} | {'Last Data (Hex)':<25}")
                print("-" * 65)
                
                for mid in sorted(msg_counts.keys()):
                    count = msg_counts[mid]
                    last_time = msg_last_seen[mid]
                    data_hex = msg_last_data[mid].hex().upper()
                    
                    # Estimate message frequency
                    hz = count / elapsed if elapsed > 0 else 0.0
                    
                    id_str = f"0x{mid:03X}"
                    print(f"{id_str:<10} | {len(msg_last_data[mid]):<4} | {count:<7} | {hz:<6.1f} | {data_hex:<25}")

    except KeyboardInterrupt:
        print("\nStopping sniffer...")
    finally:
        bus.shutdown()
        
    print("\nSniffer completed.")
    print("=" * 65)
    for mid in sorted(msg_counts.keys()):
        print(f"ID 0x{mid:03X} — Total Packets: {msg_counts[mid]}")
    print("=" * 65)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Raw CAN Bus Sniffer")
    parser.add_argument("--channel", default="can0", help="SocketCAN channel (e.g., can0, vcan0)")
    parser.add_argument("--duration", type=float, default=0, help="Sniff duration in seconds (0 = infinite)")
    args = parser.parse_args()

    run_sniffer(args.channel, args.duration)
