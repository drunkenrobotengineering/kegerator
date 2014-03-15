#!/usr/bin/python
# -*- coding: iso-8859-1 -*-

import json
import time

from lib.arduino_io import arduino, fake_arduino

from lib.dynamo_calls import record_drinks, get_amount_allowed

def handle_input(arduino, input):
    values = json.loads(input)
    if (values['FUNCTION'] == 'DRINK_DATA'):
        record_drinks(values['CODE'], values['TAP_ONE'], values['TAP_TWO'])
    elif (values['FUNCTION'] == 'CHECK_CODE'):
        arduino.send_output(str(get_amount_allowed(values['CODE'])))

if __name__ == "__main__":
    while (True) :
        try:
            arduino = arduino()
            #arduino = fake_arduino()
            while ( True ) :
                input = arduino.await_input()
                print("Received input: " + input)
                handle_input(arduino, input)
        except:
            print("An error occurred.  Sleeping for five seconds and continuing.")
            time.sleep(5)
