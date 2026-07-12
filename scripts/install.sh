#!/bin/bash
# install.sh — Setup dependencies for MoTeC CAN Telemetry Logger

set -e

echo "=========================================================="
echo " MoTeC CAN Logger — Installing Dependencies"
echo "=========================================================="

# Check if running on Linux for apt packages
if [ "$(uname)" == "Linux" ]; then
    echo "[System] Installing system tools (can-utils)..."
    sudo apt-get update
    sudo apt-get install -y can-utils
fi

# Install Python requirements via Virtual Environment (Safe for Pi OS Bookworm PEP 668)
echo "[System] Setting up Python Virtual Environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi

echo "[System] Installing Python libraries in virtual environment..."
./venv/bin/pip install --upgrade pip
./venv/bin/pip install -r requirements.txt

echo ""
echo "[Success] Installation complete."
echo "----------------------------------------------------------"
echo "To run commands, use the venv python interpreter:"
echo "  ./venv/bin/python main.py --channel can0"
echo "  ./venv/bin/python tools/can_sniffer.py --channel can0"
echo "=========================================================="
