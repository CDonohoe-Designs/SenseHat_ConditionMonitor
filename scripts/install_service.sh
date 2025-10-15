#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SERVICE_NAME="pi-sense-agent"

cat <<'UNIT' | sudo tee /etc/systemd/system/${SERVICE_NAME}.service >/dev/null
[Unit]
Description=SenseHAT MQTT Edge Agent
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
WorkingDirectory=__WORKDIR__
Environment=MQTT_HOST=192.168.1.10
Environment=MQTT_PORT=1883
Environment=MQTT_TLS=0
ExecStart=__WORKDIR__/edge/.venv/bin/python __WORKDIR__/edge/agent.py
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
UNIT

# Replace __WORKDIR__ with actual path
sudo sed -i "s|__WORKDIR__|${ROOT_DIR}|g" /etc/systemd/system/${SERVICE_NAME}.service

echo "Service installed at /etc/systemd/system/${SERVICE_NAME}.service"
echo "Run: sudo systemctl daemon-reload && sudo systemctl enable --now ${SERVICE_NAME}"