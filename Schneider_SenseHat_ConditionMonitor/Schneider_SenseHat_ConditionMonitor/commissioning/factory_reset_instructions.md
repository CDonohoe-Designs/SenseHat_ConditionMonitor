# Factory Reset Instructions (Template)

1. Stop services: `sudo systemctl stop pi-sense-agent`
2. Delete local state (if store-and-forward DB is added): `rm -f /var/lib/pi-sense-agent/data.db`
3. Clear logs: `sudo journalctl --rotate && sudo journalctl --vacuum-time=1s`
4. Reboot: `sudo reboot`