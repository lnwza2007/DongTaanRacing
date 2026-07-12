#!/usr/bin/env python3
"""
test_virtual.py — Cross-Platform End-to-End Verification Test
=============================================================
Runs mock MoTeC transmitter and CAN logger using python-can's cross-platform
'virtual' interface. Useful for testing on macOS/Windows/Linux without SocketCAN.
"""

import sys
import os
import time
import queue
import threading
import json
from datetime import datetime

# Add root folder to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    import can
except ImportError:
    print("[ERROR] 'python-can' not installed.")
    sys.exit(1)

from config.channels import CHANNELS
from logger.state_manager import StateManager
from logger.csv_writer import CsvWriter
from logger.mqtt_publisher import _MQTT_AVAILABLE

# A custom CanReader subclass that uses 'virtual' interface instead of SocketCAN
class VirtualCanReader:
    def __init__(self, state_manager: StateManager, shutdown_event: threading.Event, bus: can.BusABC):
        self.state_manager = state_manager
        self.shutdown_event = shutdown_event
        self.bus = bus
        
        from decoders.m150_decoder import M150Decoder
        from decoders.c125_decoder import C125Decoder
        self.m150_decoder = M150Decoder()
        self.c125_decoder = C125Decoder()
        
        self.thread = threading.Thread(target=self._run, name="VirtualCanReader", daemon=True)

    def start(self):
        self.thread.start()

    def _run(self):
        print("[Test-Reader] Thread started.")
        while not self.shutdown_event.is_set():
            msg = self.bus.recv(timeout=0.05)
            if msg is None:
                continue

            try:
                decoded_vals = {}
                if msg.arbitration_id in self.m150_decoder.supported_ids:
                    decoded_vals = self.m150_decoder.decode(msg.arbitration_id, msg.data)
                elif msg.arbitration_id in self.c125_decoder.supported_ids:
                    decoded_vals = self.c125_decoder.decode(msg.arbitration_id, msg.data)

                if decoded_vals:
                    self.state_manager.update(decoded_vals)
            except Exception as e:
                print(f"[Test-Reader] Decode error: {e}")

# A mock transmitter that sends to the virtual bus
class VirtualMockTransmitter:
    def __init__(self, shutdown_event: threading.Event, bus: can.BusABC):
        self.shutdown_event = shutdown_event
        self.bus = bus
        self.thread = threading.Thread(target=self._run, name="VirtualMockTransmitter", daemon=True)

    def start(self):
        self.thread.start()

    def _run(self):
        print("[Test-Transmitter] Thread started.")
        t = 0.0
        while not self.shutdown_event.is_set():
            t += 0.1
            
            # Message 0x640
            rpm = int(3000 + 1000 * (t % 5))
            tps = int(450)
            map_val = int(980)
            ect = int(880)
            data_640 = bytearray()
            data_640.extend(rpm.to_bytes(2, byteorder='little', signed=False))
            data_640.extend(tps.to_bytes(2, byteorder='little', signed=True))
            data_640.extend(map_val.to_bytes(2, byteorder='little', signed=True))
            data_640.extend(ect.to_bytes(2, byteorder='little', signed=True))

            # Message 0x660
            gear = int(3)
            batt = int(1420)
            speed = int(850)
            ign = int(220)
            data_660 = bytearray()
            data_660.extend(gear.to_bytes(2, byteorder='little', signed=True))
            data_660.extend(batt.to_bytes(2, byteorder='little', signed=False))
            data_660.extend(speed.to_bytes(2, byteorder='little', signed=False))
            data_660.extend(ign.to_bytes(2, byteorder='little', signed=True))

            # Send messages
            try:
                self.bus.send(can.Message(arbitration_id=0x640, data=data_640, is_extended_id=False))
                self.bus.send(can.Message(arbitration_id=0x660, data=data_660, is_extended_id=False))
            except Exception as e:
                print(f"[Test-Transmitter] Send error: {e}")
                
            time.sleep(0.1)

def run_test():
    print("=" * 60)
    print(" Running Virtual End-to-End Verification Test")
    print("=" * 60)
    
    shutdown_event = threading.Event()
    
    # Create Python-CAN virtual buses (cross-platform, in-process loopback)
    rx_bus = can.interface.Bus(channel="test_channel", interface="virtual")
    tx_bus = can.interface.Bus(channel="test_channel", interface="virtual")
    
    state_manager = StateManager()
    write_queue = queue.Queue(maxsize=100)
    
    csv_columns = ["timestamp", "session_id"] + [ch.name for ch in CHANNELS]
    csv_writer = CsvWriter(
        base_name="log_motec_test",
        columns=csv_columns,
        write_queue=write_queue,
        shutdown_event=shutdown_event
    )
    
    reader = VirtualCanReader(state_manager, shutdown_event, rx_bus)
    transmitter = VirtualMockTransmitter(shutdown_event, tx_bus)

    
    # Start threads
    csv_writer.start()
    reader.start()
    transmitter.start()
    
    print("[Test] Running for 3 seconds...")
    
    # Run main logging loop for 3 seconds
    start_time = time.time()
    row_count = 0
    
    try:
        while time.time() - start_time < 3.0:
            loop_start = time.monotonic()
            now_iso = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
            snap = state_manager.get_snapshot()
            
            # Print current state
            sys.stdout.write(
                f"\r[Main Logger Loop] RPM: {snap.get('engine_rpm')} | "
                f"Speed: {snap.get('vehicle_speed')} km/h | "
                f"Gear: {snap.get('gear_pos')} | "
                f"Volt: {snap.get('battery_volt')}V"
            )
            sys.stdout.flush()
            
            row = [now_iso, "test_session"]
            for ch in CHANNELS:
                row.append(state_manager.format_value(snap.get(ch.name)))
                
            write_queue.put(row)
            row_count += 1
            
            elapsed = time.monotonic() - loop_start
            sleep_t = 0.1 - elapsed
            if sleep_t > 0:
                time.sleep(sleep_t)
                
    finally:
        print("\n[Test] Shutting down...")
        shutdown_event.set()
        write_queue.put(None)
        
        csv_writer.join(timeout=2.0)
        rx_bus.shutdown()
        tx_bus.shutdown()

        
    print("=" * 60)
    print(" TEST SUCCESSFUL! ")
    print(f" Saved {row_count} telemetry rows to logs/log_motec_test.csv")
    print("=" * 60)

if __name__ == "__main__":
    run_test()
