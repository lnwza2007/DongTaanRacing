import sys
import queue
import threading
import time
import ssl
from typing import Optional

try:
    import paho.mqtt.client as mqtt
    _MQTT_AVAILABLE = True
except ImportError:
    _MQTT_AVAILABLE = False

from config.settings import (
    MQTT_USE_HIVEMQ,
    MQTT_BROKER_HIVEMQ,
    MQTT_PORT_HIVEMQ,
    MQTT_USER_HIVEMQ,
    MQTT_PASS_HIVEMQ,
    MQTT_BROKER_LOCAL,
    MQTT_PORT_LOCAL,
    MQTT_TOPIC,
    MQTT_QUEUE_SIZE
)

class MqttPublisher:
    def __init__(self, mqtt_queue: queue.Queue, shutdown_event: threading.Event):
        self.mqtt_queue = mqtt_queue
        self.shutdown_event = shutdown_event
        self.client = None
        self.thread = threading.Thread(target=self._run, name="MqttPublisher", daemon=True)

    def start(self):
        if not _MQTT_AVAILABLE:
            print("[MQTT] paho-mqtt not installed — MQTT publishing disabled.")
            return
        self.thread.start()

    def join(self, timeout=None):
        if self.thread.is_alive():
            self.thread.join(timeout)

    def _on_connect(self, client, userdata, flags, rc, *args):
        if rc == 0:
            print(f"[MQTT] Connected successfully → Topic: {MQTT_TOPIC}")
        else:
            print(f"[MQTT] Connect failed with code {rc}")

    def _on_disconnect(self, client, userdata, rc, *args):
        if rc != 0:
            print(f"[MQTT] Disconnected unexpectedly (rc={rc}) — attempting reconnection...")

    def _run(self):
        # Determine client version compatibility (Paho v1.x vs v2.x)
        try:
            # Paho MQTT v2.0+ API
            self.client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id="motec_pi_logger")
        except AttributeError:
            # Paho MQTT v1.x API
            self.client = mqtt.Client(client_id="motec_pi_logger")

        self.client.on_connect = self._on_connect
        self.client.on_disconnect = self._on_disconnect

        if MQTT_USE_HIVEMQ:
            self.client.username_pw_set(MQTT_USER_HIVEMQ, MQTT_PASS_HIVEMQ)
            # Establish secure TLS context for HiveMQ Cloud
            self.client.tls_set(cert_reqs=ssl.CERT_REQUIRED, tls_version=ssl.PROTOCOL_TLS_CLIENT)
            broker = MQTT_BROKER_HIVEMQ
            port = MQTT_PORT_HIVEMQ
        else:
            broker = MQTT_BROKER_LOCAL
            port = MQTT_PORT_LOCAL

        # Connection loop
        while not self.shutdown_event.is_set():
            try:
                print(f"[MQTT] Connecting to {broker}:{port} ...")
                self.client.connect(broker, port, keepalive=60)
                self.client.loop_start()
                break
            except Exception as exc:
                print(f"[MQTT] Connect error: {exc} — retrying in 5 s", file=sys.stderr)
                time.sleep(5)

        print("[MQTT] Publisher thread started and listening for payloads.")

        while not self.shutdown_event.is_set():
            try:
                payload = self.mqtt_queue.get(timeout=1.0)
            except queue.Empty:
                continue

            if payload is None:  # poison pill
                break

            if not self.client.is_connected():
                # Drop payload if not connected to avoid queue backup
                self.mqtt_queue.task_done()
                continue

            try:
                self.client.publish(MQTT_TOPIC, payload, qos=0, retain=False)
            except Exception as exc:
                print(f"[MQTT] Publish error: {exc}", file=sys.stderr)
            finally:
                self.mqtt_queue.task_done()

        if self.client:
            self.client.loop_stop()
            self.client.disconnect()
            
        print("[MQTT] Publisher thread exiting.")
