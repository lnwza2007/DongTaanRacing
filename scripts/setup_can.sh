#!/bin/bash
# setup_can.sh — Configures MCP2515 SocketCAN interface on Raspberry Pi at 1 Mbps

set -e

INTERFACE="can0"
BITRATE=1000000 # 1 Mbps for MoTeC

echo "=========================================================="
echo " MoTeC CAN Logger — Configuring ${INTERFACE} at 1 Mbps"
echo "=========================================================="

# Check if interface exists
if ! ip link show "$INTERFACE" > /dev/null 2>&1; then
    echo "[ERROR] Interface ${INTERFACE} not found."
    echo "        Please check if the CAN HAT is connected and overlays are loaded."
    echo "        Ensure /boot/config.txt contains the MCP2515 overlay."
    exit 1
fi

# Bring interface down first
echo "[System] Bringing ${INTERFACE} down..."
sudo ip link set "$INTERFACE" down || true

# Configure bitrate and bring interface up
echo "[System] Setting bitrate to ${BITRATE} bps and bringing interface up..."
sudo ip link set "$INTERFACE" type can bitrate "$BITRATE"
sudo ip link set "$INTERFACE" up

# Show status
echo "[Success] SocketCAN interface status:"
ip -details link show "$INTERFACE"
echo "=========================================================="
