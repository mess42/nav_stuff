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
    In rad. Ranges from 0 to 2*pi.
      0    means that Point 2 is north of Point 1.
    0.5 pi means that Point 2 is east  of Point 1.
        pi means that Point 2 is south of Point 1.
    1.5 pi means that Point 2 is west  of Point 1.
    """
    
    lat1 = lat1_deg * pi/180
    lat2 = lat2_deg * pi/180
    phi = (lon2_deg-lon1_deg) *pi/180

    # approximation: distance between points 1 and 2 is small compared to earth's curvature
    azim_rad = np.arctan2(phi * np.cos(lat1), lat2-lat1)
        
    return azim_rad

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

def calc_regression_slope(x,y):
    """
    @brief: makes a linear regression and delivers the slope.
    
    @param x: (1d numpy array of float)
              Data point x-values.
    @peram y: (1d numpy array of float)
              Data point y-values
              Array must have same shape as x.
              
    Regression model is y = m * x + n
    where m and n are optimised for minimum square error compared to the data points.
    
    @return m: (float)
               Slope of the linear reagression.
    """
    x = np.array(x)
    y = np.array(y)
    N = len(x)
    m = (sum(x*y) - sum(x)*sum(y)/N) / (sum(x**2) - (sum(x))**2/N)
    return m

def calc_speed( lat_track, lon_track, time_track, no_datapoints_for_average = 5):
    if len(time_track) >= no_datapoints_for_average:
        dlat_per_dt = calc_regression_slope(
                         x=time_track[-no_datapoints_for_average:],
                         y=lat_track[-no_datapoints_for_average:]
                         )
        dlon_per_dt = calc_regression_slope(
                         x=time_track[-no_datapoints_for_average:],
                         y=lon_track[-no_datapoints_for_average:]
                         )
    else:
        dlat_per_dt = 0
        dlon_per_dt = 0
        
    v_azim_in_rad = calc_azim(
                          lat1_deg = lat_track[-1], 
                          lon1_deg = lon_track[-1], 
                          lat2_deg = lat_track[-1]+dlat_per_dt,
                          lon2_deg = lon_track[-1]+dlon_per_dt,
                          )
    abs_v_in_m_per_s = haversine_distance(
                          lat1_deg = lat_track[-1], 
                          lon1_deg = lon_track[-1], 
                          lat2_deg = lat_track[-1]+dlat_per_dt,
                          lon2_deg = lon_track[-1]+dlon_per_dt,
                          )

    return dlat_per_dt, dlon_per_dt, v_azim_in_rad, abs_v_in_m_per_s
