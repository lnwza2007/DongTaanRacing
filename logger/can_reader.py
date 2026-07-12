import sys
import time
import threading
from typing import Set

try:
    import can
except ImportError:
    print("[ERROR] 'python-can' library is not installed.")
    print("        Run:  pip install python-can")
    sys.exit(1)

from config.can_ids import MOTEC_CAN_IDS
from decoders.m150_decoder import M150Decoder
from decoders.c125_decoder import C125Decoder
from logger.state_manager import StateManager

class CanReader:
    def __init__(self, channel: str, bitrate: int, state_manager: StateManager, shutdown_event: threading.Event):
        self.channel = channel
        self.bitrate = bitrate
        self.state_manager = state_manager
        self.shutdown_event = shutdown_event
        
        # Instantiate decoders
        self.m150_decoder = M150Decoder()
        self.c125_decoder = C125Decoder()
        
        self.thread = threading.Thread(target=self._run, name="CANReader", daemon=True)

    def start(self):
        self.thread.start()

    def join(self, timeout=None):
        self.thread.join(timeout)

    def _run(self):
        print(f"[CAN] Starting reader on '{self.channel}' at {self.bitrate/1e6:.1f} Mbps...")

        while not self.shutdown_event.is_set():
            bus = None
            try:
                # Use socketcan for Linux/Pi, or virtual CAN if specified
                if self.channel.startswith("vcan"):
                    bus = can.interface.Bus(channel=self.channel, interface="socketcan")
                else:
                    bus = can.interface.Bus(channel=self.channel, interface="socketcan", bitrate=self.bitrate)
                
                print(f"[CAN] Connected to '{self.channel}' successfully.")

                while not self.shutdown_event.is_set():
                    msg = bus.recv(timeout=0.05)
                    if msg is None:
                        continue

                    # Filter for MoTeC CAN IDs only
                    if msg.arbitration_id not in MOTEC_CAN_IDS:
                        continue

                    try:
                        # Decode depending on source device
                        decoded_vals = {}
                        if msg.arbitration_id in self.m150_decoder.supported_ids:
                            decoded_vals = self.m150_decoder.decode(msg.arbitration_id, msg.data)
                        elif msg.arbitration_id in self.c125_decoder.supported_ids:
                            decoded_vals = self.c125_decoder.decode(msg.arbitration_id, msg.data)

                        if decoded_vals:
                            self.state_manager.update(decoded_vals)

                    except Exception as exc:
                        print(f"[CAN] Decode error on ID 0x{msg.arbitration_id:03X}: {exc}", file=sys.stderr)

            except (can.CanError, OSError) as exc:
                print(f"[CAN] Bus error: {exc}. Reconnecting in 2 s...", file=sys.stderr)
            except Exception as exc:
                print(f"[CAN] Unexpected error: {exc}", file=sys.stderr)
            finally:
                if bus:
                    try:
                        bus.shutdown()
                    except Exception:
                        pass

            if not self.shutdown_event.is_set():
                time.sleep(2.0)

        print("[CAN] Reader thread exiting.")
