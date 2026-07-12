# CAN ID Definitions for MoTeC M150 & C125

# M150 ECU General Transmit stream (standard MoTeC GP firmware layout)
M150_PRIMARY     = 0x640   # RPM, TPS, MAP, ECT
M150_SECONDARY   = 0x648   # Oil Pres, Oil Temp, IAT, Fuel Pres
M150_FUEL_LAMBDA = 0x650   # Lambda 1, Lambda 2, Fuel Temp, EGT
M150_GEAR_SPEED  = 0x660   # Gear, Battery Volt, Speed, Ign Advance

# C125 Dash Transmit (default placeholders or user-configured IDs)
C125_LAP_DATA    = 0x700   # Lap Number, Lap Time (ms), Buttons
C125_STATUS      = 0x701   # Alarm states, display status

# Set of all relevant CAN IDs for quick filtering/decoding
MOTEC_CAN_IDS = {
    M150_PRIMARY,
    M150_SECONDARY,
    M150_FUEL_LAMBDA,
    M150_GEAR_SPEED,
    C125_LAP_DATA,
    C125_STATUS
}
