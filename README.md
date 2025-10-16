# SenseHAT Condition Monitor (Raspberry Pi)

**Owner:** Caoilte Donohoe  
**Generated:** 2025-10-16

A small Raspberry Pi + Sense HAT node that publishes room conditions and device health, shows a simple dashboard, and can feed other systems.

## Project Overview
Raspberry Pi + Sense HAT edge agent publishing metrics (**Temp, Humidity, Pressure, 3-axis accel**) to MQTT and exposing a `/health` endpoint. Node-RED dashboard provides live gauges and a temperature trend chart.

## Current Status (v0.2.0)
- Agent runs as systemd service: `pi-sense-agent`
- MQTT topic: `spBv1.0/sensehat/DDATA/pi-edge` (**QoS1, retained**)
- Health endpoint: `http://<pi-ip>:8080/health`
- Node-RED dashboard: `http://<pi-ip>:1880/ui`
- Modbus-TCP server (optional): **port 5020**

## Run / Verify (quick)
```bash
mosquitto_sub -t 'spBv1.0/sensehat/DDATA/pi-edge' -v
curl http://<pi-ip>:8080/health
# then open the dashboard
# http://<pi-ip>:1880/ui
```

## System Architecture
Sensors → Pi agent → MQTT → Dashboard/other systems.  
Simple `/health` page for quick checks.  
Optional: Modbus‑TCP view for building systems (same readings).

![Architecture placeholder](docs/images/SenseHAT_Architecture.png)

## Implementation (lite)
- **Edge Agent:** auto-starts, restarts on failure; reads temp/humidity/pressure/3-axis accel + device health.
- **MQTT:** Sparkplug-style topics, QoS1 + retained for reliable last-value display.
- **HTTP & Dashboard:** `/health` shows "OK" + uptime; Node-RED `/ui` shows live gauges + temperature trend.
- **Modbus-TCP (optional):** small register map for BMS/SCADA (port 5020).

## Register Map (Modbus‑TCP)
| Register | Signal            | Units  | Notes           |
|--------:|--------------------|--------|-----------------|
|   30001 | env.temp_c         | 0.1 °C | Temperature ×10 |
|   30002 | env.humidity_pct   | 0.1 %  | Humidity ×10    |
|   30003 | env.pressure_hpa   | 0.1 hPa| Pressure ×10    |
|   30010 | sys.cpu_temp_c     | 0.1 °C | CPU temp ×10    |
|   30020 | sys.uptime_s_low   | s      | Low word        |
|   30021 | sys.uptime_s_high  | s      | High word       |

## Notes / Quirks
- Sense HAT temperature can read slightly high from CPU heat; a simple compensation is used.
- Pressure may briefly return 0 on first reads; agent guards against bogus values.

## Next (as needed)
- Store-and-forward buffer (SQLite) for offline periods.
- Service unit for Modbus‑TCP server.
- TLS + credentials for MQTT in production.

## Quick Install (outline)
1. **Clone or copy** this repo onto the Pi.
2. Copy `config/config.example.yaml` to `/etc/pi-sense-agent/config.yaml` and edit the MQTT/server details.
3. Copy `deploy/pi-sense-agent.service` to `/etc/systemd/system/` and enable:
   ```bash
   sudo systemctl daemon-reload
   sudo systemctl enable --now pi-sense-agent
   sudo systemctl status pi-sense-agent
   ```
4. Import the Node-RED flow from `node-red/flows_sensehat.json` (Menu → Import) and open `/ui`.

## Repo Structure
```
SenseHAT-Edge/
├─ agent/                 # (your Python agent here)
├─ config/
│  └─ config.example.yaml
├─ deploy/
│  └─ pi-sense-agent.service
├─ docs/
│  └─ images/
│     └─ SenseHAT_Architecture.png (placeholder)
├─ node-red/
│  └─ flows_sensehat.json
└─ README.md
```

## License
MIT — see [LICENSE](LICENSE).
