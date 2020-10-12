#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import serial
import decode_nmea



ser = serial.Serial(
        port="/dev/ttyUSB1", 
        timeout = 0.2
        )
ser.isOpen()

for i in range(20):
    sentence = ser.readline().decode("utf-8")
    print(sentence)
    if sentence.startswith("$GPRMC"):
        print( decode_nmea.decode_gprmc_sentence(sentence) )

ser.close()
