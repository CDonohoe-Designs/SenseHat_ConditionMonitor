#!/usr/bin/env bash
set -euo pipefail

# Resolve repo root from this script's location
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"

echo "[install] Repo: $REPO_DIR"

echo "[1/5] Create/update Python venv and install deps"
python3 -m venv "$REPO_DIR/edge/.venv"
"$REPO_DIR/edge/.venv/bin/pip" install --upgrade pip
if [ -f "$REPO_DIR/requirements.txt" ]; then
  "$REPO_DIR/edge/.venv/bin/pip" install -r "$REPO_DIR/requirements.txt"
fi

echo "[2/5] Install/refresh systemd unit"
# Try to install unit from repo; if missing, write a minimal one
if [ -f "$REPO_DIR/deploy/pi-sense-agent.service" ]; then
  sudo install -D -m 0644 "$REPO_DIR/deploy/pi-sense-agent.service" /etc/systemd/system/pi-sense-agent.service
else
  echo "[install] Base unit missing in repo, writing minimal unit"
  sudo tee /etc/systemd/system/pi-sense-agent.service >/dev/null <<'UNIT'
[Unit]
Description=SenseHAT Edge Agent
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/SenseHat_ConditionMonitor
ExecStart=/usr/bin/python3 /home/pi/SenseHat_ConditionMonitor/edge/agent.py
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
UNIT
fi

echo "[3/5] Write override to pin to this repo + venv"
sudo mkdir -p /etc/systemd/system/pi-sense-agent.service.d
sudo tee /etc/systemd/system/pi-sense-agent.service.d/override.conf >/dev/null <<OVR
[Service]
WorkingDirectory=$REPO_DIR
# reset then set ExecStart to use repo venv python + agent path
ExecStart=
ExecStart=$REPO_DIR/edge/.venv/bin/python $REPO_DIR/edge/agent.py
# Optional: load environment values if present
EnvironmentFile=-/etc/pi-sense-agent/agent.env
OVR

echo "[4/5] Ensure env template exists (won't overwrite existing)"
sudo install -d -m 0755 /etc/pi-sense-agent
if [ ! -f /etc/pi-sense-agent/agent.env ]; then
  if [ -f "$REPO_DIR/config/ENV.example" ]; then
    sudo cp "$REPO_DIR/config/ENV.example" /etc/pi-sense-agent/agent.env
  else
    sudo tee /etc/pi-sense-agent/agent.env >/dev/null <<'ENV'
# MQTT connection (edit these for your broker)
MQTT_HOST=127.0.0.1
MQTT_PORT=1883
MQTT_TLS=0
# MQTT_USERNAME=
# MQTT_PASSWORD=
ENV
  fi
  echo "[install] Wrote /etc/pi-sense-agent/agent.env (edit as needed)"
fi

echo "[5/5] Reload + enable service"
sudo systemctl daemon-reload
sudo systemctl enable --now pi-sense-agent

echo
echo "Status:"
systemctl --no-pager --full status pi-sense-agent || true
echo
echo "Logs (tail -50):"
journalctl -u pi-sense-agent -n 50 --no-pager || true

echo
echo "Quick verify:"
echo "  curl http://127.0.0.1:8080/health"
echo "  mosquitto_sub -t 'spBv1.0/sensehat/DDATA/pi-edge' -v | head"
