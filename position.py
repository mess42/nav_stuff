#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""

"""
import serial
import datetime

class PositionProvider(object):
    def __init__(self, **params ):
        """
        Baseclass to connect to position provider services.
        """
        self.latitude  = float("nan") # degree, positive is North
        self.longitude = float("nan") # degree, positive is East
        self.time      = None         # datetime of last sensor update
        self.velocity  = 0            # in m/s
        self.azimuth   = 0            # azimuth of velocity in degree
        
        self.is_connected = False
        self.connect( **params )
            
    def connect(self, **params):
        raise NotImplementedError()
        
    def disconnect(self):
        raise NotImplementedError()
        
    def update_position(self):
        success = False
        raise NotImplementedError()
        return success

class PositionSerialNMEA(PositionProvider):
    """
    Connect to a NMEA device on a serial port.
    """
    def connect(self, serial_port, timeout = 1.0):
        if self.is_connected:
            self.disconnect()
        self.serial_connection = serial.Serial( port=serial_port, timeout = timeout )
        self.serial_connection.isOpen() # wait until open
        self.is_connected = True
    
    def disconnect(self):
        if self.is_connected:
            self.serial_connection.close()
            self.is_connected = False
        
    def update_position(self):
        sentence = self.serial_connection.readline().decode("utf-8")
        is_active = False
        if sentence.startswith("$GPRMC"):
            data = sentence[:-3].split(",")[1:]
            is_active = ( data[1] == "A" )
            if is_active:
                self.time      = self.__raw_to_time__(raw_date = data[8], raw_time = data[0])
                self.latitude  = self.__raw_angle_to_decimal__( data[2] ) * (1 - 2 * (data[3] == "S") )
                self.longitude = self.__raw_angle_to_decimal__( data[4] ) * (1 - 2 * (data[5] == "W") )
                self.velocity  = self.__raw_to_float__(data[6]) * 1.852 / 3.6
                self.azimuth   = self.__raw_to_float__(data[7])
        return is_active
        
    def __raw_to_time__(self, raw_date, raw_time):
        sec = float(raw_time[4:])
        time = datetime.datetime(
                    year        = int(raw_date[4:]), 
                    month       = int(raw_date[2:4]), 
                    day         = int(raw_date[:2]), 
                    hour        = int(raw_time[:2]), 
                    minute      = int(raw_time[2:4]), 
                    second      = int(sec), 
                    microsecond = int( 1000000 * (sec % 1))
                    )
        return time     
        
    def __raw_angle_to_decimal__(self, raw):
        """
        Converts a NMEA longitude or latitude string to a decimal representation.
        
        @param raw (str) "" or numeric digits
               First digits are degrees.
                 Latitude has 2 digits with full degrees (ranges from 0 to 90)
                 Longitude has 3 digits with full degrees (ranges from 0 to 180)
               Last 2 digits in front of the point are arc minutes.
               Digits behind the point are decimal fractions of arc minutes
               "DDMM.mmmmm"
               The sign of the angle is not part of the input string.
               The sign must be extracted from the separate "N","S","W", or "E" flag.
        @return alpha (float)
               In degrees.
               Floating point number in the decimal system.
               An input of "" is converted to nan.
        """
        alpha = float("nan")
        if len(raw) > 0:
            rawfloat = float(raw)
            int_abs = rawfloat // 100
            alpha = int_abs  + (rawfloat - 100 * int_abs) / 60
        return alpha
    
    def __raw_to_float__(self, raw):
        """
        Converts a string representation of float (in the decimal system) to a float.
        
        @param raw (str)
        @return flo (float)
               An input of "" is converted to nan.          
        """
        flo = float("nan")
        if len(raw) > 0:
            flo = float(raw)
        return flo