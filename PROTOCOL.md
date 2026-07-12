# MoTeC M150 & C125 CAN Protocol Reference

This document details the CAN protocol messages used by the MoTeC M150 ECU and the MoTeC C125 Dash Logger.

## CAN Bitrate
- **1,000,000 bps (1 Mbps)**
- Standard frame format (11-bit identifiers)
- Byte order: **Little Endian (Intel)**

---

## M150 ECU Standard Broadcast (M1 General Template)

Standard MoTeC GP (General Purpose) packages transmit engine data on CAN IDs `0x640` through `0x670`.

### Message 0x640 (Primary Engine Data)
| Byte Offset | Data Type | Channel Name | Scaling / Formula | Unit | Description |
|---|---|---|---|---|---|
| 0 - 1 | UInt16 | `engine_rpm` | `raw * 1` | rpm | Engine Speed |
| 2 - 3 | Int16 | `throttle_pos` | `raw * 0.1` | % | Throttle Position (TPS) |
| 4 - 5 | Int16 | `manifold_pres` | `raw * 0.1` | kPa | Manifold Absolute Pressure (MAP) |
| 6 - 7 | Int16 | `coolant_temp` | `raw * 0.1` | °C | Engine Coolant Temperature (ECT) |

### Message 0x648 (Secondary Engine Sensors)
| Byte Offset | Data Type | Channel Name | Scaling / Formula | Unit | Description |
|---|---|---|---|---|---|
| 0 - 1 | Int16 | `oil_pres` | `raw * 0.1` | kPa | Engine Oil Pressure |
| 2 - 3 | Int16 | `oil_temp` | `raw * 0.1` | °C | Engine Oil Temperature |
| 4 - 5 | Int16 | `intake_temp` | `raw * 0.1` | °C | Intake Air Temperature (IAT) |
| 6 - 7 | Int16 | `fuel_pres` | `raw * 0.1` | kPa | Fuel Pressure |

### Message 0x650 (Fuel & Lambda Status)
| Byte Offset | Data Type | Channel Name | Scaling / Formula | Unit | Description |
|---|---|---|---|---|---|
| 0 - 1 | UInt16 | `lambda_1` | `raw * 0.001` | La | Exhaust Lambda Sensor 1 |
| 2 - 3 | UInt16 | `lambda_2` | `raw * 0.001` | La | Exhaust Lambda Sensor 2 |
| 4 - 5 | Int16 | `fuel_temp` | `raw * 0.1` | °C | Fuel Temperature |
| 6 - 7 | Int16 | `exhaust_temp` | `raw * 0.1` | °C | Exhaust Gas Temperature (EGT) |

### Message 0x660 (Gearbox & Battery)
| Byte Offset | Data Type | Channel Name | Scaling / Formula | Unit | Description |
|---|---|---|---|---|---|
| 0 - 1 | Int16 | `gear_pos` | `raw` (0=N, 1-6=Gears, -1=R) | - | Current Gear Position |
| 2 - 3 | UInt16 | `battery_volt` | `raw * 0.01` | V | ECU Battery Voltage |
| 4 - 5 | UInt16 | `vehicle_speed` | `raw * 0.1` | km/h | Vehicle Speed |
| 6 - 7 | Int16 | `ign_advance` | `raw * 0.1` | ° | Ignition Advance Angle |

---

## C125 Dash Transmit (Custom / Dash Manager configured)

The MoTeC C125 display transmits additional telemetry data such as lap timer information.

### Message 0x700 (Lap Timing & Driver Inputs)
| Byte Offset | Data Type | Channel Name | Scaling / Formula | Unit | Description |
|---|---|---|---|---|---|
| 0 - 1 | UInt16 | `lap_number` | `raw` | - | Current Lap Number |
| 2 - 5 | UInt32 | `lap_time_ms` | `raw * 1` | ms | Last Lap Time in milliseconds |
| 6 | UInt8 | `dash_button_1` | `raw` (0=Off, 1=On) | - | Dash button 1 status |
| 7 | UInt8 | `dash_button_2` | `raw` (0=Off, 1=On) | - | Dash button 2 status |
