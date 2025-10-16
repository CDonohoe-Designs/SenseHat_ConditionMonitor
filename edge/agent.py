#!/usr/bin/env python3
import os, time, json, ssl, threading
from sense_hat import SenseHat
import paho.mqtt.client as mqtt
from flask import Flask, jsonify

# ---------- Config from environment ----------
BROKER   = os.getenv("MQTT_HOST", "127.0.0.1")
PORT     = int(os.getenv("MQTT_PORT", "1883"))
USE_TLS  = os.getenv("MQTT_TLS", "0") == "1"
TOPIC    = os.getenv("MQTT_TOPIC", "spBv1.0/sensehat/DDATA/pi-edge")
INTERVAL = float(os.getenv("PUBLISH_INTERVAL_S", "2.0"))
TEMP_WARN= float(os.getenv("TEMP_WARN_C", "35"))

# ---------- MQTT client ----------
client = mqtt.Client(client_id=os.getenv("MQTT_CLIENT_ID", "pi-edge-001"))
if USE_TLS:
    client.tls_set(cert_reqs=ssl.CERT_REQUIRED)
client.connect(BROKER, PORT, keepalive=30)
client.loop_start()

# ---------- Sense HAT ----------
sense = SenseHat()
sense.clear()

def cpu_temp_c():
    try:
        with open("/sys/class/thermal/thermal_zone0/temp") as f:
            return float(f.read())/1000.0
    except Exception:
        return None

def led(rgb):
    r,g,b = rgb
    sense.clear(r,g,b)

# ---------- /health HTTP endpoint ----------
health = {"started": int(time.time()), "last_publish": 0, "topic": TOPIC}
app = Flask(__name__)

@app.get("/health")
def healthz():
    now = int(time.time())
    return jsonify({
        "ok": True,
        "uptime_s": now - health["started"],
        "last_publish": health["last_publish"],
        "topic": health["topic"],
        "broker": f"{BROKER}:{PORT}",
        "tls": USE_TLS,
    }), 200

def run_health():
    # Port 8080 (adjust if you need)
    app.run(host="0.0.0.0", port=8080, threaded=True)

# Start health server in background
threading.Thread(target=run_health, daemon=True).start()

def payload():
    # Temperature with simple CPU heat compensation
    t_raw = sense.get_temperature()
    cpu = cpu_temp_c()
    if cpu is not None:
        # empirical nudge; keeps it simple for demo
        t_corr = t_raw - (cpu - t_raw) / 1.5
    else:
        t_corr = t_raw

    h = sense.get_humidity()

    # Pressure guard (avoid bogus zeros)
    p_raw = sense.get_pressure()
    p = round(p_raw, 1) if p_raw and p_raw > 50 else None

    accel = sense.get_accelerometer_raw()
    return {
        "ts": int(time.time()*1000),
        "metrics": {
            "temp_c": round(t_corr, 2),
            "hum_pct": round(h, 2),
            "press_hpa": p,
            "ax": round(accel.get('x', 0.0), 4),
            "ay": round(accel.get('y', 0.0), 4),
            "az": round(accel.get('z', 0.0), 4),
        }
    }

try:
    while True:
        data = payload()
        # LED status rule
        if data["metrics"]["temp_c"] >= TEMP_WARN:
            led((255, 140, 0))  # amber
        else:
            led((0, 128, 0))    # green

        health["last_publish"] = int(time.time())
        client.publish(TOPIC, json.dumps(data), qos=1, retain=True)
        time.sleep(INTERVAL)
except KeyboardInterrupt:
    pass
finally:
    sense.clear()
    client.loop_stop()
