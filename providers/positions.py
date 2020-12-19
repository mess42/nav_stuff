#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
This file defines position providers.
A position provider delivers the current position and handles sensor communication.
"""

import gi
gi.require_version('Geoclue', '2.0')
from gi.repository import Geoclue

import numpy as np
import serial
import datetime

import helpers.angles

def get_mapping_of_names_to_classes():
    """
    @brief: Pointers to all classes that shall be usable.
    (no base classes)
    
    @return d (dict)
    """
    d = {"PositionSerialNMEA": PositionSerialNMEA,
         "PositionGeoClue": PositionGeoClue,
         "PositionSimulation": PositionSimulation,
        }
    return d

class PositionProvider(object):
    def __init__(self, **params ):
        """
        Baseclass to connect to position provider services.
        """
        self.latitude  = 0 # degree, positive is North
        self.longitude = 0 # degree, positive is East
        self.time      = 0 # unix timestamp of last sensor update
        self.velocity  = 0 # in m/s
        self.heading   = 0 # heading of velocity in degree
        self.is_connected = False
        
        self.connect( **params )
        self.update_position()
            
    def connect(self, **params):
        """
        Connect to a positioning service, configure, allocate and lock resources.
        """
        raise NotImplementedError()
        
    def disconnect(self):
        raise NotImplementedError()
        
    def update_position(self):
        success = False
        raise NotImplementedError()
        return success

class PositionSerialNMEA(PositionProvider):
    def connect(self, serial_port, timeout = 1.0):
        """
        Connect to a NMEA device on a serial port.
        """
        if self.is_connected:
            self.disconnect()
        self.serial_connection = serial.Serial( port=serial_port, timeout = timeout )
        self.serial_connection.isOpen() # wait until open
        self.is_connected = True
    
    def disconnect(self):
        """
        Close the serial connection (free the serial port).
        """
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
                self.heading   = self.__raw_to_float__(data[7])
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
                    ).timestamp()
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
    
class PositionGeoClue(PositionProvider):
    """
    Thanks to 
    https://howtotrainyourrobot.com/building-a-mobile-app-for-linux-part-4-gps-mobile-tracking/
    https://www.freedesktop.org/software/geoclue/docs/libgeoclue/GClueLocation.html
    """

    def connect(self):
        self.clue = Geoclue.Simple.new_sync('something',
                                            Geoclue.AccuracyLevel.NEIGHBORHOOD,
                                            None
                                            )
        self.is_connected = True
        
    def disconnect(self):
        self.clue = None
        self.is_connected = False
        
    def update_position(self):
        location = self.clue.get_location()        
        self.time      = location.get_property("timestamp")
        self.latitude  = location.get_property('latitude')
        self.longitude = location.get_property('longitude')
        self.velocity  = location.get_property("speed")
        self.heading   = location.get_property("heading")
        #location.get_property("accuracy") )            
        return True

    
class PositionSimulation(PositionProvider):
    def __init__(self, **params ):
        
        self.velocity = 10 # m/s
        
        import json
        from scipy.interpolate import interp1d
        f = open("providers/position_simulation_data.json","r")
        dic = json.load(f)
        f.close()
                
        self.__path_lat_deg = np.array(dic["lat_deg"])
        self.__path_lon_deg = np.array(dic["lon_deg"])
        delta_in_m = helpers.angles.haversine_distance(lat1_deg = self.__path_lat_deg[1:], 
                                                    lon1_deg = self.__path_lon_deg[1:], 
                                                    lat2_deg = self.__path_lat_deg[:-1], 
                                                    lon2_deg = self.__path_lon_deg[:-1],
                                                   )
        covered_dist_in_m = np.cumsum(delta_in_m)
        start_time = datetime.datetime.now().timestamp() - 28100
        self.__path_time = start_time + np.hstack([[0],covered_dist_in_m]) / self.velocity
        
        self.lat_interpolator = interp1d(self.__path_time, self.__path_lat_deg)
        self.lon_interpolator = interp1d(self.__path_time, self.__path_lon_deg)

        PositionProvider.__init__(self, **params)


    def connect(self):
        self.is_connected = True
        
    def disconnect(self):
        self.is_connected = False
        
    def update_position(self):
        self.time = datetime.datetime.now().timestamp()
        
        epsilon = 1 # time to calculate the difference quotient for the heading
        
        if self.time <= self.__path_time[0]:
            self.latitude  = self.__path_lat_deg[0]
            self.longitude = self.__path_lon_deg[0]
            self.heading   = 0
        elif self.time >= self.__path_time[-1] - epsilon:
            self.latitude  = self.__path_lat_deg[-1]
            self.longitude = self.__path_lon_deg[-1]
            self.heading   = 0
        else:
            self.latitude  = self.lat_interpolator(self.time)
            self.longitude = self.lon_interpolator(self.time)
            lat2           = self.lat_interpolator(self.time+epsilon)
            lon2           = self.lon_interpolator(self.time+epsilon)
            airline        = helpers.angles.calc_properties_of_airline(lat1_deg=self.latitude, lon1_deg=self.longitude, lat2_deg=lat2, lon2_deg=lon2)
            self.heading   = airline["azimuth_from_point_1_towards_2_deg"]
        return True
