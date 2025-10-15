# Modbus Holding Register Map

Base address 40001 (shown 1-based). Pymodbus uses 0-based offsets internally.

| Address | Name      | Units | Scale | Type  | Notes |
|--------:|-----------|-------|------:|-------|------|
| 40001   | temp_c    | °C    | ×100  | int16 | 27.43°C → 2743 |
| 40002   | hum_pct   | %RH   | ×100  | int16 | 44.90% → 4490 |
| 40003   | press_hpa | hPa   | ×1    | int16 | 1006 hPa → 1006 |
| 40004   | ax        | g     | ×1000 | int16 | 0.981 g → 981 |
| 40005   | ay        | g     | ×1000 | int16 | |
| 40006   | az        | g     | ×1000 | int16 | |

**Polling example:** read 6 holding registers starting at 40001.