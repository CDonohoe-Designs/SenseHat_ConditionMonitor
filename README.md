#SenseHAT Condition Monitor (EcoStruxure‑friendly)

**Objective:** A small but professional Raspberry Pi + Sense HAT edge agent that publishes sensor data (Temp/Humidity/Pressure/IMU) over MQTT and exposes a Modbus‑TCP server so BMS/SCADA/EcoStruxure can poll values. Includes commissioning docs, Node‑RED dashboard stub, and service script.

## Features
- MQTT publisher (QoS1, retain) — Sparkplug‑style topic by default.
- Modbus‑TCP server with a simple holding‑register map.
- LED matrix status (green/amber/red), joystick to acknowledge alarms (todo).
- Store‑and‑forward ready (SQLite placeholder), /health API (todo).
- Clean repo for portfolio use.

## Quick start (edge MQTT publisher)
```bash
cd edge
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
# set your broker; use 1883 for plain or 8883 with TLS
export MQTT_HOST=192.168.1.10
export MQTT_PORT=1883
export MQTT_TLS=0   # set 1 to enable TLS
python agent.py
```

**Payload example:**
```json
{
  "ts": 1739599999123,
  "metrics": {"temp_c": 27.4, "hum_pct": 44.9, "press_hpa": 1006.2, "ax": -0.01, "ay": 0.00, "az": 0.98}
}
```

## Run Modbus‑TCP server
```bash
cd edge && source .venv/bin/activate
pip install -r requirements.txt
python modbus_server.py  # listens on 0.0.0.0:5020 (non‑privileged)
```
Poll holding registers from any Modbus client at port **5020**.

## Register map (short)
| Address | Name        | Units  | Scale | Notes |
|--------:|-------------|--------|------:|-------|
| 40001   | temp_c      | °C     | ×100  | int16 |
| 40002   | hum_pct     | %RH    | ×100  | int16 |
| 40003   | press_hpa   | hPa    | ×1    | int16 (truncate) |
| 40004   | ax          | g      | ×1000 | int16 |
| 40005   | ay          | g      | ×1000 | int16 |
| 40006   | az          | g      | ×1000 | int16 |

Full details: `commissioning/register_map_modbus.md`

## Autostart as a service (agent)
```bash
cd scripts
sudo ./install_service.sh
sudo systemctl enable --now pi-sense-agent.service
journalctl -u pi-sense-agent -f
```

## Repo layout
```
edge/                 # Python edge agent + servers
commissioning/        # Register map, network plan, test checklist
dashboards/node-red/  # Example Node‑RED flow (importable JSON)
docs/                 # Diagrams & PDFs for your portfolio
scripts/              # Service install helper
```

---

## ✅ Current Status (v0.1.0)
- MVP working on Raspberry Pi 3 (Bookworm) with Sense HAT (I²C enabled).
- MQTT JSON publish every ~2s.
- Modbus-TCP holding registers 40001–40006 on port **5020**.
- LED: green = normal, amber = temp > threshold.

## Verify
```bash
# MQTT stream
mosquitto_sub -t 'spBv1.0/sensehat/DDATA/pi-edge' -v

# Optional: Modbus test (expects 6 registers)
python3 -c 'from pymodbus.client import ModbusTcpClient as C;c=C("127.0.0.1",port=5020);r=c.read_holding_registers(0,6);print(getattr(r,"registers",r));c.close()'
Made for interview alignment with Schneider Electric’s IoT Project Engineer remit.
