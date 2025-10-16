#!/usr/bin/env python3
import time, threading
from sense_hat import SenseHat
from pymodbus.server import StartTcpServer
from pymodbus.datastore import ModbusSlaveContext, ModbusServerContext
from pymodbus.payload import BinaryPayloadBuilder, Endian
from pymodbus.device import ModbusDeviceIdentification
from pymodbus.transaction import ModbusRtuFramer

# Holding register layout (0-based offsets for library; +1 in Modbus docs)
ADDR_TEMP = 0  # 40001
ADDR_HUM  = 1  # 40002
ADDR_PRES = 2  # 40003
ADDR_AX   = 3  # 40004
ADDR_AY   = 4  # 40005
ADDR_AZ   = 5  # 40006

store = ModbusSlaveContext(hr=dict())
context = ModbusServerContext(slaves=store, single=True)
sense = SenseHat()

def update_loop():
    while True:
        try:
            t  = int(round(sense.get_temperature() * 100))     # x100
            h  = int(round(sense.get_humidity() * 100))        # x100
            p  = int(sense.get_pressure())                     # x1
            acc = sense.get_accelerometer_raw()
            ax = int(round(acc['x'] * 1000))                   # x1000 g
            ay = int(round(acc['y'] * 1000))
            az = int(round(acc['z'] * 1000))

            hr = store.getValues(3, 0, count=16) or [0]*16  # 3 == holding registers
            # expand list if needed
            if len(hr) < 16:
                hr = hr + [0]*(16-len(hr))
            hr[ADDR_TEMP] = t & 0xFFFF
            hr[ADDR_HUM]  = h & 0xFFFF
            hr[ADDR_PRES] = p & 0xFFFF
            hr[ADDR_AX]   = ax & 0xFFFF
            hr[ADDR_AY]   = ay & 0xFFFF
            hr[ADDR_AZ]   = az & 0xFFFF
            store.setValues(3, 0, hr)
        except Exception:
            # Keep running even if sensor hiccups
            pass
        time.sleep(1)

def main():
    updater = threading.Thread(target=update_loop, daemon=True)
    updater.start()

    identity = ModbusDeviceIdentification()
    identity.VendorName  = "CDonohoe-Designs"
    identity.ProductCode = "SENSEHAT-CM"
    identity.VendorUrl   = "https://github.com/CDonohoe-Designs"
    identity.ProductName = "SenseHAT Condition Monitor"
    identity.ModelName   = "SH-CM-01"
    identity.MajorMinorRevision = "1.0"

    # Non-privileged port (502 requires root); bind all interfaces
    StartTcpServer(context, identity=identity, address=("0.0.0.0", 5020))

if __name__ == "__main__":
    main()