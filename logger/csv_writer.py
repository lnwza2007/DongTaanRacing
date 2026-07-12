import os
import csv
import sys
import queue
import threading
from typing import List
from config.settings import LOG_DIR, MAX_FILE_BYTES, FLUSH_EVERY_N

class CsvWriter:
    def __init__(self, base_name: str, columns: List[str], write_queue: queue.Queue, shutdown_event: threading.Event):
        self.base_name = base_name
        self.columns = columns
        self.write_queue = write_queue
        self.shutdown_event = shutdown_event
        
        self.log_dir = LOG_DIR
        os.makedirs(self.log_dir, exist_ok=True)
        
        self.part = 1
        self.file = None
        self.writer = None
        self.row_count = 0
        
        self._open_file()
        self.thread = threading.Thread(target=self._run, name="CsvWriter", daemon=True)

    def start(self):
        self.thread.start()

    def join(self, timeout=None):
        self.thread.join(timeout)

    def _current_path(self):
        if self.part == 1:
            fname = f"{self.base_name}.csv"
        else:
            fname = f"{self.base_name}_part{self.part}.csv"
        return os.path.join(self.log_dir, fname)

    def _open_file(self):
        path = self._current_path()
        is_new = not os.path.exists(path) or os.path.getsize(path) == 0
        
        self.file = open(path, mode="a", newline="", encoding="utf-8")
        self.writer = csv.writer(self.file)
        
        if is_new:
            self.writer.writerow(self.columns)
            self.file.flush()
            
        print(f"[Writer] Logging data to: {path}")

    def _rotate(self):
        self.close()
        self.part += 1
        self.row_count = 0
        self._open_file()
        print(f"[Writer] Rotated to part {self.part}")

    def write_row(self, row: List[str]):
        try:
            # Check size limits for rotation
            if os.path.getsize(self._current_path()) >= MAX_FILE_BYTES:
                self._rotate()
                
            self.writer.writerow(row)
            self.row_count += 1
            
            # Periodically flush to disk to ensure data is saved on power loss
            if self.row_count % FLUSH_EVERY_N == 0:
                self.file.flush()
                os.fsync(self.file.fileno())
                
        except Exception as exc:
            print(f"[Writer] Write error: {exc}", file=sys.stderr)

    def close(self):
        if self.file and not self.file.closed:
            try:
                self.file.flush()
                os.fsync(self.file.fileno())
            finally:
                self.file.close()
                print(f"[Writer] Closed: {self._current_path()}")

    def _run(self):
        print("[Writer] File writer thread started.")
        while True:
            try:
                row = self.write_queue.get(timeout=1.0)
            except queue.Empty:
                if self.shutdown_event.is_set():
                    break
                continue

            if row is None:  # poison pill
                break

            self.write_row(row)
            self.write_queue.task_done()

        # Drain the remaining queue
        while not self.write_queue.empty():
            try:
                row = self.write_queue.get_nowait()
                if row is not None:
                    self.write_row(row)
                self.write_queue.task_done()
            except queue.Empty:
                break

        self.close()
        print("[Writer] File writer thread exiting.")
