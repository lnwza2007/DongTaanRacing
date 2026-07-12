import threading
import time
import math
from typing import Dict, Any
from config.channels import CHANNELS
from config.settings import STALE_TIMEOUT

class StateManager:
    def __init__(self):
        self.lock = threading.Lock()
        
        # Initialize state with all configured channel names set to None
        self.state: Dict[str, Any] = {ch.name: None for ch in CHANNELS}
        
        # Keep track of the last time each channel was updated
        self.last_update: Dict[str, float] = {}

    def update(self, data: Dict[str, Any]):
        now = time.time()
        with self.lock:
            for key, val in data.items():
                if key in self.state:
                    self.state[key] = val
                    self.last_update[key] = now

    def get_snapshot(self) -> Dict[str, Any]:
        now = time.time()
        with self.lock:
            snapshot = dict(self.state)
            updates = dict(self.last_update)
        
        # Stale data filter
        for key in snapshot.keys():
            last_ts = updates.get(key)
            if last_ts is None or (now - last_ts) > STALE_TIMEOUT:
                snapshot[key] = None
                
        return snapshot

    @staticmethod
    def format_value(v: Any) -> str:
        if v is None:
            return "NaN"
        if isinstance(v, float) and math.isnan(v):
            return "NaN"
        if isinstance(v, float):
            return f"{v:.4f}"
        return str(v)
