#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import datetime

def raw_angle_to_decimal(raw):
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

def raw_to_float(raw):
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

def raw_to_time(raw_date, raw_time):
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
        

def decode_gprmc_sentence(sentence):
    """
    Converts a RMC NMEA sentence to a python dict.
    
    @param sentence (str)
           sentence must start with "$GPRMC,"
           
    @return dec (dict)
           keys always present are:
           "is_active" (bool)
                   GPS device was able to get an active location fix.
                   
           optional keys are:
           "time": (datetime.datetime object)
           "latitude" (float)
                   in degree.
                   Ranges from -90 (south pole) to +90 (north pole).
           "longitude" (float)
                   in degree.
                   Ranges from -180 to 180. Positive means east of London.
           "speed" (float)
                   speed above ground in m/s.
           "azimuth" (float)
                   angle of the velocity track.

    """
    data = sentence[:-3].split(",")[1:]

    dec = {"is_active": ( data[1] == "A" ) }
    
    if dec["is_active"]:
        dec["time"]      = raw_to_time(raw_date = data[8], raw_time = data[0])
        dec["latitude"]  = raw_angle_to_decimal( data[2] ) * (1 - 2 * (data[3] == "S") )
        dec["longitude"] = raw_angle_to_decimal( data[4] ) * (1 - 2 * (data[5] == "W") )
        dec["speed"]     = raw_to_float(data[6]) * 1.852 / 3.6
        dec["azimuth"]   = raw_to_float(data[7])

    return dec


if __name__ == "__main__":
    
    sentence = "$GPRMC,,V,,,,,,,,,,"
    print( decode_gprmc_sentence(sentence) )