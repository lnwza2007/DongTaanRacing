# MoTeC M150 & C125 CAN Telemetry Logger

Raspberry Pi 4 CAN Bus CSV Logger and MQTT Publisher for MoTeC systems.

## Overview
This system uses a **Raspberry Pi 4** with an **MCP2515 SPI CAN HAT** to read real-time CAN bus telemetry from a MoTeC M150 ECU and a MoTeC C125 Dash Logger.
- Logs all incoming messages to standard rotated CSV files (`logs/`)
- Publishes real-time telemetry over MQTT (HiveMQ or local Mosquitto)
- Provides sniffer and mock simulation tools for offline testing.

## Wiring Guide
The CAN bus signals are routed through a physical **RJ45** connector.
> **WARNING**: This is NOT Ethernet. Do not plug this connector into an Ethernet port.

### Custom RJ45 Pinout
| RJ45 Pin | Wire Color (T568B) | Signal | Note |
|---|---|---|---|
| 1 | Orange/White | **CAN High** | Twisted with Pin 2 |
| 2 | Orange | **CAN Low** | Twisted with Pin 1 |
| 3 | Green/White | **GND** | Signal Ground Reference |
| 4 | Blue | Reserved | - |
| 5 | Blue/White | Reserved | - |
| 6 | Green | Shield | Chassis ground (one end only) |
| 7 | Brown/White | GND | - |
| 8 | Brown | Power (V+) | Optional power supply |

Ensure a **120 Ohm** terminating resistor is active on the CAN HAT if it is at the end of the bus.

## Installation
Run the installer script:
```bash
bash scripts/install.sh
```

Ensure SocketCAN is configured on `can0` at **1 Mbps (1,000,000 baud)**:
```bash
bash scripts/setup_can.sh
```

## Running the Logger
To start the logger:
```bash
python main.py --channel can0 --session race_day_1
```

To run offline testing using a virtual CAN interface:
```bash
# Terminal 1: Start mock MoTeC transmitter
python tools/mock_motec.py --channel vcan0

# Terminal 2: Run logger on virtual interface
python main.py --channel vcan0 --session offline_test
```
