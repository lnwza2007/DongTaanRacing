from dataclasses import dataclass
from typing import List, Dict
from config.can_ids import (
    M150_PRIMARY,
    M150_SECONDARY,
    M150_FUEL_LAMBDA,
    M150_GEAR_SPEED,
    C125_LAP_DATA
)

@dataclass
class ChannelDef:
    name: str
    can_id: int
    byte_offset: int
    byte_length: int
    signed: bool
    multiplier: float
    offset: float
    unit: str
    byte_order: str = 'little'  # MoTeC default is Intel/little endian

# Full list of channel definitions for MoTeC logger
CHANNELS: List[ChannelDef] = [
    # --- Message 0x640: Primary Engine Data ---
    ChannelDef(
        name="engine_rpm",
        can_id=M150_PRIMARY,
        byte_offset=0,
        byte_length=2,
        signed=False,
        multiplier=1.0,
        offset=0.0,
        unit="rpm"
    ),
    ChannelDef(
        name="throttle_pos",
        can_id=M150_PRIMARY,
        byte_offset=2,
        byte_length=2,
        signed=True,
        multiplier=0.1,
        offset=0.0,
        unit="%"
    ),
    ChannelDef(
        name="manifold_pres",
        can_id=M150_PRIMARY,
        byte_offset=4,
        byte_length=2,
        signed=True,
        multiplier=0.1,
        offset=0.0,
        unit="kPa"
    ),
    ChannelDef(
        name="coolant_temp",
        can_id=M150_PRIMARY,
        byte_offset=6,
        byte_length=2,
        signed=True,
        multiplier=0.1,
        offset=0.0,
        unit="°C"
    ),

    # --- Message 0x648: Secondary Engine Sensors ---
    ChannelDef(
        name="oil_pres",
        can_id=M150_SECONDARY,
        byte_offset=0,
        byte_length=2,
        signed=True,
        multiplier=0.1,
        offset=0.0,
        unit="kPa"
    ),
    ChannelDef(
        name="oil_temp",
        can_id=M150_SECONDARY,
        byte_offset=2,
        byte_length=2,
        signed=True,
        multiplier=0.1,
        offset=0.0,
        unit="°C"
    ),
    ChannelDef(
        name="intake_temp",
        can_id=M150_SECONDARY,
        byte_offset=4,
        byte_length=2,
        signed=True,
        multiplier=0.1,
        offset=0.0,
        unit="°C"
    ),
    ChannelDef(
        name="fuel_pres",
        can_id=M150_SECONDARY,
        byte_offset=6,
        byte_length=2,
        signed=True,
        multiplier=0.1,
        offset=0.0,
        unit="kPa"
    ),

    # --- Message 0x650: Fuel & Lambda Status ---
    ChannelDef(
        name="lambda_1",
        can_id=M150_FUEL_LAMBDA,
        byte_offset=0,
        byte_length=2,
        signed=False,
        multiplier=0.001,
        offset=0.0,
        unit="La"
    ),
    ChannelDef(
        name="lambda_2",
        can_id=M150_FUEL_LAMBDA,
        byte_offset=2,
        byte_length=2,
        signed=False,
        multiplier=0.001,
        offset=0.0,
        unit="La"
    ),
    ChannelDef(
        name="fuel_temp",
        can_id=M150_FUEL_LAMBDA,
        byte_offset=4,
        byte_length=2,
        signed=True,
        multiplier=0.1,
        offset=0.0,
        unit="°C"
    ),
    ChannelDef(
        name="exhaust_temp",
        can_id=M150_FUEL_LAMBDA,
        byte_offset=6,
        byte_length=2,
        signed=True,
        multiplier=0.1,
        offset=0.0,
        unit="°C"
    ),

    # --- Message 0x660: Gearbox & Battery ---
    ChannelDef(
        name="gear_pos",
        can_id=M150_GEAR_SPEED,
        byte_offset=0,
        byte_length=2,
        signed=True,
        multiplier=1.0,
        offset=0.0,
        unit=""
    ),
    ChannelDef(
        name="battery_volt",
        can_id=M150_GEAR_SPEED,
        byte_offset=2,
        byte_length=2,
        signed=False,
        multiplier=0.01,
        offset=0.0,
        unit="V"
    ),
    ChannelDef(
        name="vehicle_speed",
        can_id=M150_GEAR_SPEED,
        byte_offset=4,
        byte_length=2,
        signed=False,
        multiplier=0.1,
        offset=0.0,
        unit="km/h"
    ),
    ChannelDef(
        name="ign_advance",
        can_id=M150_GEAR_SPEED,
        byte_offset=6,
        byte_length=2,
        signed=True,
        multiplier=0.1,
        offset=0.0,
        unit="°"
    ),

    # --- Message 0x700: C125 Lap Timing & Buttons ---
    ChannelDef(
        name="lap_number",
        can_id=C125_LAP_DATA,
        byte_offset=0,
        byte_length=2,
        signed=False,
        multiplier=1.0,
        offset=0.0,
        unit=""
    ),
    ChannelDef(
        name="lap_time_ms",
        can_id=C125_LAP_DATA,
        byte_offset=2,
        byte_length=4,
        signed=False,
        multiplier=1.0,
        offset=0.0,
        unit="ms"
    ),
    ChannelDef(
        name="dash_button_1",
        can_id=C125_LAP_DATA,
        byte_offset=6,
        byte_length=1,
        signed=False,
        multiplier=1.0,
        offset=0.0,
        unit=""
    ),
    ChannelDef(
        name="dash_button_2",
        can_id=C125_LAP_DATA,
        byte_offset=7,
        byte_length=1,
        signed=False,
        multiplier=1.0,
        offset=0.0,
        unit=""
    ),
]

# Map channel names to definitions for quick lookup
CHANNEL_MAP: Dict[str, ChannelDef] = {c.name: c for c in CHANNELS}

# Group channels by CAN ID
CHANNELS_BY_ID: Dict[int, List[ChannelDef]] = {}
for c in CHANNELS:
    CHANNELS_BY_ID.setdefault(c.can_id, []).append(c)
