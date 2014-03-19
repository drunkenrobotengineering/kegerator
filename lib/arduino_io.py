#!/usr/bin/python

import json
import serial
from serial import *
import time
import random

class arduino():
#    serial_port = "/dev/tty.arduino"
    serial_port = "/dev/tty.usbmodem1411"
    def __init__(self, timeout=None, writeTimeout=5):
        self.serial = serial.Serial(port=self.serial_port, baudrate=19200)
        time.sleep(3)

    def await_input(self):
        input = self.serial.readline()
        print("Received serial input: " + input)
        return input

    def send_output(self, output):
        print("Sending serial output: " + str(output))
        self.serial.write(output)

class fake_arduino():
    # For testing when I don't have an Arduino handy
    one = 0.0
    two = 50.0
    def __init__(self):
        pass

    def await_input(self):
        delay = random.randint(10,30)
        time.sleep(delay)
        self.one = self.one + 20
        self.two = self.two * 1.02
        return '{"CODE":"12345abcde", "TAP_ONE": 123, "TAP_TWO":234}'
        drink_info={"1":{},"2":{}}
        drink_info["1"]["c"] = self.one
        drink_info["2"]["c"] = self.two
        return drink_info

    def send_output(self, output):
        self.serial.write(output)
