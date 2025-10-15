# Network Plan (Template)

- **Pi hostname:** pi-sense-001
- **LAN/VLAN:** e.g., OT VLAN 20
- **IP mode:** DHCP reservation (MAC: xx:xx:xx:xx:xx:xx)
- **Broker:** 192.168.1.10:1883 (TLS 8883 in production)
- **Modbus server:** Pi listens on 5020/TCP
- **Firewall openings:** 1883/8883 (outbound), 5020 (inbound on BMS side if needed)