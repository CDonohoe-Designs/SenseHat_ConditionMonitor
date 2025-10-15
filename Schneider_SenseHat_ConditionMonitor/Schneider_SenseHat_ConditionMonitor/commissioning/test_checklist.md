# Commissioning / Test Checklist

1. **Power & Network**
   - Pi boots and gets IP via DHCP.
   - `ping <Pi IP>` from laptop succeeds.

2. **Time Sync**
   - `timedatectl` shows correct time (affects message timestamps).

3. **MQTT Publisher**
   - Set broker env and run `edge/agent.py`.
   - On broker machine: `mosquitto_sub -t 'spBv1.0/sensehat/DDATA/pi-edge' -v` prints JSON every 2s.

4. **Modbus Server**
   - Run `edge/modbus_server.py`. From client, read holding registers 40001..40006 at port 5020.

5. **Alarms**
   - Warm the Pi (e.g., hand over case) to trip `TEMP_WARN_C` and observe LED amber.

6. **Node-RED (optional)**
   - Import `dashboards/node-red/flows_sensehat.json`. Show gauges + status.

7. **Security**
   - For remote/broker: enable TLS (MQTT_TLS=1, port 8883). Use unique creds per device.