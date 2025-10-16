# SenseHAT Condition Monitor (Raspberry Pi)

**Owner:** Caoilte Donohoe  
**Generated:** 2025-10-16

A small Raspberry Pi + Sense HAT node that publishes room conditions and device health, shows a simple dashboard, and can feed other systems.

---

## TL;DR — One-Command Install on the Pi
```bash
# from the repo root on the Pi
chmod +x deploy/scripts/install.sh
deploy/scripts/install.sh
```

This will:
- create/update a Python venv in **edge/.venv** and install `requirements.txt`
- install/refresh the **pi-sense-agent** systemd unit + override pointing at this repo/venv
- write `/etc/pi-sense-agent/agent.env` (template) for MQTT settings if missing
- enable & start **pi-sense-agent**

**Verify:**
```bash
mosquitto_sub -t 'spBv1.0/sensehat/DDATA/pi-edge' -v | head
curl http://<pi-ip>:8080/health
# open the dashboard:
# http://<pi-ip>:1880/ui
```

---

## Project Overview
Raspberry Pi + Sense HAT edge agent publishing metrics (**Temp, Humidity, Pressure, 3-axis accel**) to MQTT and exposing a `/health` endpoint. Node-RED dashboard provides live gauges and a temperature trend chart.

## Current Status (v0.2.0)
- Agent runs as systemd service: **`pi-sense-agent`** (auto-start, restart on failure)
- MQTT topic: `spBv1.0/sensehat/DDATA/pi-edge` (**QoS1, retained**)
- Health endpoint: `http://<pi-ip>:8080/health`
- Node-RED dashboard: `http://<pi-ip>:1880/ui`
- Modbus-TCP server (optional): **port 5020**

---

## System Architecture
Sensors → Pi agent → MQTT → Dashboard/other systems.  
Simple `/health` page for quick checks.  
Optional: Modbus-TCP view for building systems (same readings).

![Architecture placeholder](docs/images/SenseHAT_Architecture.png)

---

## Implementation (lite)
- **Edge Agent:** `edge/agent.py` — auto-starts, restarts on failure; reads temp/humidity/pressure/3-axis accel + device health.
- **MQTT:** Sparkplug-style topics, **QoS1 + retained** for reliable last-value display.
- **HTTP & Dashboard:** `/health` shows “OK” + uptime; Node-RED `/ui` shows live gauges + temperature trend.
- **Config via env:** edit `/etc/pi-sense-agent/agent.env` (see `config/ENV.example`).
- **Modbus-TCP (optional):** small register map for BMS/SCADA (port 5020).

---

## Register Map (Modbus-TCP)
| Register | Signal            | Units  | Notes           |
|--------:|--------------------|--------|-----------------|
|   30001 | env.temp_c         | 0.1 °C | Temperature ×10 |
|   30002 | env.humidity_pct   | 0.1 %  | Humidity ×10    |
|   30003 | env.pressure_hpa   | 0.1 hPa| Pressure ×10    |
|   30010 | sys.cpu_temp_c     | 0.1 °C | CPU temp ×10    |
|   30020 | sys.uptime_s_low   | s      | Low word        |
|   30021 | sys.uptime_s_high  | s      | High word       |

---

## Notes / Quirks
- Sense HAT temperature can read slightly high from CPU heat; a simple compensation is used.
- Pressure may briefly return 0 on first reads; agent guards against bogus values.

---

## Quick Install (manual outline)
If you don’t use the one-command installer:

1. **Clone or copy** this repo onto the Pi.
2. Create a venv & install deps:
   ```bash
   python3 -m venv edge/.venv
   edge/.venv/bin/pip install -r requirements.txt
   ```
3. Install base unit and add an override pointing to this repo/venv:
   ```bash
   sudo install -D -m 0644 deploy/pi-sense-agent.service /etc/systemd/system/pi-sense-agent.service
   sudo mkdir -p /etc/systemd/system/pi-sense-agent.service.d
   sudo tee /etc/systemd/system/pi-sense-agent.service.d/override.conf >/dev/null <<EOF
   [Service]
   WorkingDirectory=$(pwd)
   ExecStart=
   ExecStart=$(pwd)/edge/.venv/bin/python $(pwd)/edge/agent.py
   EnvironmentFile=-/etc/pi-sense-agent/agent.env
   EOF
   ```
4. Create the env file and set MQTT host/port:
   ```bash
   sudo install -d -m 0755 /etc/pi-sense-agent
   sudo cp config/ENV.example /etc/pi-sense-agent/agent.env
   ```
5. Enable & start:
   ```bash
   sudo systemctl daemon-reload
   sudo systemctl enable --now pi-sense-agent
   sudo systemctl status pi-sense-agent --no-pager
   ```
6. Import the Node-RED flow from `node-red/flows_sensehat.json` (Menu → Import) and open `/ui`.

---

## Service Management
```bash
systemctl status pi-sense-agent --no-pager
sudo systemctl restart pi-sense-agent
journalctl -u pi-sense-agent -n 100 --no-pager
```

---

## Repository Structure
```
edge/                    # agent.py (your running agent)
node-red/
  └─ flows_sensehat.json # exported flow (no creds file)
deploy/
  ├─ pi-sense-agent.service
  └─ scripts/
     └─ install.sh       # one-command installer
config/
  └─ ENV.example         # environment variables template
docs/
  └─ images/
     └─ SenseHAT_Architecture.png (placeholder)
requirements.txt
.gitignore               # excludes venv, secrets, Node-RED cred file
README.md
```

---

## License
MIT — see [LICENSE](LICENSE).
