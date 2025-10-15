#!/usr/bin/env python3
import os, time, json, ssl
from sense_hat import SenseHat
import paho.mqtt.client as mqtt

BROKER = os.getenv("MQTT_HOST", "127.0.0.1")
PORT   = int(os.getenv("MQTT_PORT", "1883"))
USE_TLS= os.getenv("MQTT_TLS", "0") == "1"
TOPIC  = os.getenv("MQTT_TOPIC", "spBv1.0/sensehat/DDATA/pi-edge")
INTERVAL = float(os.getenv("PUBLISH_INTERVAL_S", "2.0"))
TEMP_WARN = float(os.getenv("TEMP_WARN_C", "35"))

client = mqtt.Client(client_id=os.getenv("MQTT_CLIENT_ID", "pi-edge-001"))
if USE_TLS:
    client.tls_set(cert_reqs=ssl.CERT_REQUIRED)

client.connect(BROKER, PORT, keepalive=30)
client.loop_start()

sense = SenseHat()
sense.clear()

def led(color):
    r,g,b = color
    sense.clear(r,g,b)

def payload():
    t = sense.get_temperature()
    h = sense.get_humidity()
    p = sense.get_pressure()
    accel = sense.get_accelerometer_raw()
    return {
        "ts": int(time.time()*1000),
        "metrics": {
            "temp_c": round(t,2),
            "hum_pct": round(h,2),
            "press_hpa": round(p,2),
            "ax": round(accel['x'], 4),
            "ay": round(accel['y'], 4),
            "az": round(accel['z'], 4),
        }
    }

try:
    while True:
        data = payload()
        if data["metrics"]["temp_c"] >= TEMP_WARN:
            led((255, 140, 0))  # amber
        else:
            led((0, 128, 0))    # green
        client.publish(TOPIC, json.dumps(data), qos=1, retain=True)
        time.sleep(INTERVAL)
except KeyboardInterrupt:
    pass
finally:
    sense.clear()
    client.loop_stop()