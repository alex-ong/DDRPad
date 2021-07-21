"""
Serial gui for showing current
floating point values for the pad
you can also send a magic packet
back to the pad for it to re-write it's
eeprom so you can store pad sensitivity inside
"""

# try to import pyserial

try:
    import serial
except ImportError:
    print("Please check readme.md for installation and running instructions!")
    input("Press enter to continue...")
    import sys

    sys.exit()

from serial.tools import list_ports
import tkinter as tk
import sys
import time
import json

START_DEBUG = 1
STOP_DEBUG = 2
WRITE_SENS = 3
ENDIAN = "big"


def get_ports():
    """
    returns ["COM3", "COM4" ...]
    """
    items = list(list_ports.comports())
    for item in items:
        print(item.device)
        return [item.device for item in items]


def load_config():
    with open("config.json", "r") as data:
        data = json.load(data)
    return data


def write_config(config):
    lines = json.dumps(config, indent=4)
    with open("config.json", "w") as data:
        data.writelines(lines)


def get_saved_port():
    config = load_config()
    return config["port"]


def set_saved_port(value):
    config = load_config()
    config["port"] = value
    write_config(config)


def get_sens():
    config = load_config()
    return config["arrows"]


def set_sens_config(value):
    config = load_config()
    config["arrows"] = value
    write_config(config)


class SerialPort:
    def __init__(self):
        self.port = None

    def connect(self):
        config = load_config()
        print("attempting to connect to ", config["port"])
        self.port = serial.Serial(config["port"])
        print("connected!")

    def disconnect(self):
        self.port.close()
        self.port = None

    def read(self):
        if self.port is None:
            return []
        lines = []
        lines_read = 0
        while self.port.in_waiting and lines_read < 100:
            data = self.port.read_until()
            lines.append(data)
            lines_read += 1
        return lines

    def port_write_sens(self):
        config = load_config()
        values = config["arrows"]
        values = [value[0] for value in values]
        values = [value.to_bytes(2, ENDIAN) for value in values]
        header = WRITE_SENS.to_bytes(1, ENDIAN)
        values = [header] + values
        values = b"".join(values)
        print(values)
        self.port.write(values)

    def port_debug_on(self):
        self.port.write(START_DEBUG.to_bytes(1, ENDIAN))

    def port_debug_off(self):
        self.port.write(STOP_DEBUG.to_bytes(1, ENDIAN))


if __name__ == "__main__":
    mainloop()
