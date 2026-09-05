#!/usr/bin/env bash
set -euo pipefail
echo "[SETUP] Configuring Docker bridge network for distributed honeypots..."
if command -v docker >/dev/null 2>&1 && docker info >/dev/null 2>&1; then
    docker network create --subnet=172.28.0.0/16 honeypot_net 2>/dev/null || true
    echo "[SETUP] Docker network honeypot_net active."
else
    echo "[SETUP] Docker daemon inactive. Native host networking will be utilized."
fi
