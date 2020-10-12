#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import numpy as np
from numpy import pi

def calc_azim(lat1_deg , lon1_deg , lat2_deg , lon2_deg):
    """
    @brief Calculate the azimuth of an air line from point 1 to 2 on a sphere surface.
    
    @param lat1_deg (float) Latitude  of Point 1
    @paran lon1_deg (float) Longitude of Point 1
    @paran lat2_deg (float) Latitude  of Point 2
    @param lon2_deg (float) Longitude of Point 2
    Latitudes are in degree and range from -90 (south pole) to +90 (north pole)
    Longitudes are in degree and rage from -180 to 180.
    Positive Longitude means east of London.
    
    @return azim_deg (float)
    In degree. Ranges from 0 to 360.
      0 means that Point 2 is north of Point 1.
     90 means that Point 2 is east  of Point 1.
    180 means that Point 2 is south of Point 1.
    270 means that Point 2 is west  of Point 1.
    """
    
    lat1 = lat1_deg * pi/180
    lat2 = lat2_deg * pi/180
    phi = (lon2_deg-lon1_deg) *pi/180

    ny = np.cos(lat1) * np.sin(lat2) - np.sin(lat1) * np.cos(lat2) * np.cos(phi)
    nx_plus_nz_squared = (np.cos(lat2) * np.sin(phi))**2
    
    azim_deg = np.arccos( ny / np.sqrt(ny**2+nx_plus_nz_squared) ) * 180 /pi
    if phi < 0:
        azim_deg = 360 - azim_deg 
    return azim_deg
