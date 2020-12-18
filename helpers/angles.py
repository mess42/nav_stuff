#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import numpy as np
from numpy import pi


def hav(theta_rad):
    """
    Haversine function.
    
    @param theta_rad (float)
           Angle in rad.
          
    @return h (float)
    """
    return np.sin(0.5 * theta_rad)**2


def haversine_distance(lat1_deg, lon1_deg, lat2_deg, lon2_deg, r = 6365000 ):
    """
    Calculates the air line distance between 2 points on the surface of a sphere.
    When applying the formula to calculations of distances on earth,
    one is confronted with the fact that earth would be more 
    accurately modelled by an oblate ellipsoid than by a sphere.
    The Haversine distance has systematic deviations from the actual distance.
    @param lat1_deg (float) Latitude  of Point 1 in degree.
    @param lon1_deg (float) Longitude of Point 1 in degree.
    @param lat2_deg (float) Latitude  of Point 2 in degree.
    @param lon2_deg (float) Longitude of Point 2 in degree.
    @param r        (float) Sphere radius.
                            The default value is an average 
                            of earth's polar and equatorial radius in meters.
    
    @return d (float)
           Distance between the 2 points. 
           Unit is the same as the unit of r.
    """
    lon1 = lon1_deg * pi / 180.0
    lat1 = lat1_deg * pi / 180.0
    lon2 = lon2_deg * pi / 180.0
    lat2 = lat2_deg * pi / 180.0
    tmp = hav(lat2-lat1) + np.cos(lat1) * np.cos(lat2) * hav(lon2-lon1)
    d = 2 * r * np.arcsin( np.sqrt(tmp) )
    return d

def calc_angle_C(a,b,c, lon1_deg, lon2_deg):
    cosC = ( np.cos(c) - np.cos(a) * np.cos(b) ) / ( np.sin(a) * np.sin(b) )
    cosC = min( 1, cosC )
    cosC = max(-1, cosC )
    C = np.arccos(cosC)
    
    if lon1_deg > lon2_deg:
        C = 2*pi - C

    return C

def calc_properties_of_airline(lat1_deg, lon1_deg, lat2_deg, lon2_deg, r = 6365000):
    """
    @brief properties of a direct air line between 2 points on a sphere.
    
    Azimuth is the compass direction, that is the angle between north and the target.
        
    Consider a "triangle" on a unit sphere with edges on point1, point2, and the north pole.
    Apply the spherical law of cosines.
    https://en.wikipedia.org/wiki/Spherical_law_of_cosines
    """
    a = haversine_distance(lat1_deg, lon1_deg, lat2_deg, lon2_deg, r = 1 )
    b = (90 - lat1_deg) * pi / 180
    c = (90 - lat2_deg) * pi / 180
    
    C = calc_angle_C( a=a, b=b, c=c, lon1_deg=lon1_deg, lon2_deg=lon2_deg )
    B = calc_angle_C( a=a, b=c, c=b, lon1_deg=lon2_deg, lon2_deg=lon1_deg )
    
    return {"distance_m": a * r,
            "azimuth_from_point_1_towards_2_deg": C * 180/pi,
            "azimuth_from_point_2_towards_1_deg": B * 180/pi,
            }
    
def azimuth_to_nesw_string(azim_deg):
    dir_to_name = {337.5:"North-West", 292.5:"West", 247.5:"South-West", 202.5:"South", 157.5:"South-East", 112.5:"East", 67.5:"North-East", 22.5 :"North" }
    borders = np.array(list(dir_to_name.keys()), dtype=float)
    direction  = borders[-1]
    for b in borders:
        if azim_deg % 360 <= b:
            direction = b
    nesw_string = dir_to_name[direction]
    return nesw_string
