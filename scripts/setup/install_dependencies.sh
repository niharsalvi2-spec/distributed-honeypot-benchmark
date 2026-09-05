#!/usr/bin/env bash
set -euo pipefail
echo "[SETUP] Installing Python benchmark requirements..."
pip install -r requirements.txt
pip install -r requirements-dev.txt
echo "[SETUP] Dependencies installed successfully."
