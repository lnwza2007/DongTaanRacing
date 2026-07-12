#!/usr/bin/env python3
"""
main.py — MoTeC M150 & C125 Telemetry Logger
============================================
Launches threads for reading CAN frames, writing to CSV, and publishing over MQTT.
"""

import argparse
import json
import queue
import signal
import sys
import time
import threading
from datetime import datetime

from config.settings import CAN_CHANNEL, CAN_BITRATE, SAMPLE_HZ, SAMPLE_INTERVAL, MQTT_PUBLISH_HZ
from config.channels import CHANNELS
from logger.state_manager import StateManager
from logger.can_reader import CanReader
from logger.csv_writer import CsvWriter
from logger.mqtt_publisher import MqttPublisher, _MQTT_AVAILABLE

shutdown_event = threading.Event()

def handle_signal(sig, frame):
    print(f"\n[System] Signal {sig} received. Shutting down gracefully...")
    shutdown_event.set()

def main():
    # Parsing Command Line Arguments
    parser = argparse.ArgumentParser(description="MoTeC CAN Telemetry Logger")
    parser.add_argument("--channel", default=CAN_CHANNEL, help=f"SocketCAN interface (default: {CAN_CHANNEL})")
    parser.add_argument("--session", default=None, help="Session name/identifier (default: auto)")
    args = parser.parse_args()

    channel = args.channel
    session_id = args.session if args.session else f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

    # Setup signal handlers for clean exit
    signal.signal(signal.SIGINT, handle_signal)
    signal.signal(signal.SIGTERM, handle_signal)

    print("=" * 60)
    print("      MoTeC CAN Telemetry Logger v1.0")
    print("=" * 60)
    print(f" CAN Channel : {channel}")
    print(f" CAN Bitrate : {CAN_BITRATE / 1e6:.1f} Mbps")
    print(f" Session ID  : {session_id}")
    print(f" Sample Rate : {SAMPLE_HZ} Hz")
    print("=" * 60)

    # Initialize State
    state_manager = StateManager()

    # Setup queues
    write_queue = queue.Queue(maxsize=500)
    mqtt_queue = queue.Queue(maxsize=100)

    # Define CSV schema dynamically from configured channels
    csv_columns = ["timestamp", "session_id"] + [ch.name for ch in CHANNELS]

    # Generate unique log file base name
    base_log_name = f"log_motec_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    # Initialize and start CSV writer
    csv_writer = CsvWriter(
        base_name=base_log_name,
        columns=csv_columns,
        write_queue=write_queue,
        shutdown_event=shutdown_event
    )
    csv_writer.start()

    # Initialize and start MQTT publisher
    mqtt_publisher = MqttPublisher(
        mqtt_queue=mqtt_queue,
        shutdown_event=shutdown_event
    )
    mqtt_publisher.start()

    # Initialize and start CAN reader
    can_reader = CanReader(
        channel=channel,
        bitrate=CAN_BITRATE,
        state_manager=state_manager,
        shutdown_event=shutdown_event
    )
    can_reader.start()

    # --- MAIN LOOP (Fixed rate sampling & logging) ---
    print(f"[Main] Logging started at {SAMPLE_HZ} Hz. Press Ctrl+C to stop.\n")
    row_count = 0

    try:
        while not shutdown_event.is_set():
            loop_start = time.monotonic()
            now_iso = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]

            # Get snapshot of all channels with stale data checking
            snap = state_manager.get_snapshot()

            # Construct CSV row
            row = [now_iso, session_id]
            for ch in CHANNELS:
                row.append(state_manager.format_value(snap.get(ch.name)))

            # Push row to CSV queue
            try:
                write_queue.put_nowait(row)
            except queue.Full:
                print("[Main] CSV write queue full! Dropping row.", file=sys.stderr)

            # Publish snapshot over MQTT
            if _MQTT_AVAILABLE:
                try:
                    payload = json.dumps({
                        "timestamp": now_iso,
                        "session_id": session_id,
                        "data": {k: v for k, v in snap.items() if v is not None}
                    }, separators=(',', ':'))
                    mqtt_queue.put_nowait(payload)
                except queue.Full:
                    pass  # Drop payload to avoid blocking loop if connection lag occurs
                except Exception as exc:
                    print(f"[Main] MQTT publish fail: {exc}", file=sys.stderr)

            row_count += 1

            # Output console dashboard every 1s (10 updates at 10Hz/20Hz)
            if row_count % int(SAMPLE_HZ) == 0:
                sys.stdout.write(
                    f"\r\033[K[{now_iso}] "
                    f"RPM: {snap.get('engine_rpm', 'NaN')} | "
                    f"Speed: {snap.get('vehicle_speed', 'NaN')} km/h | "
                    f"TPS: {snap.get('throttle_pos', 'NaN')}% | "
                    f"Gear: {snap.get('gear_pos', 'NaN')} | "
                    f"Volt: {snap.get('battery_volt', 'NaN')}V | "
                    f"Lap: {snap.get('lap_number', 'NaN')} | "
                    f"Time: {snap.get('lap_time_ms', 'NaN')} ms"
                )
                sys.stdout.flush()

            # Drift-corrected sleep
            elapsed = time.monotonic() - loop_start
            sleep_t = SAMPLE_INTERVAL - elapsed
            if sleep_t > 0:
                time.sleep(sleep_t)

    except Exception as exc:
        print(f"\n[Main] Critical failure: {exc}", file=sys.stderr)
        shutdown_event.set()

    # Graceful shutdown process
    print("\n[Main] Exiting main loop...")
    shutdown_event.set()

    # Send poison pills
    write_queue.put(None)
    mqtt_queue.put(None)

    # Join threads
    csv_writer.join(timeout=5.0)
    mqtt_publisher.join(timeout=3.0)
    can_reader.join(timeout=2.0)

    print("[System] Telemetry logger stopped safely.")

if __name__ == "__main__":
    main()
