#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
https://wiki.openstreetmap.org/wiki/Slippy_map_tilenames#Python
"""

import numpy as np
from numpy import pi

class SlippyMapTile(object):
    def __init__(self, lat_deg, lon_deg):
        zoom = 18
        x,y = self.deg2num(lat_deg=lat_deg, lon_deg=lon_deg, zoom=zoom)
        self.url = self.__make_url__( x = x, y = y, zoom = zoom )
        self.north_lat, self.west_lon = self.num2deg(x  ,y  ,zoom)
        self.south_lat, self.east_lon = self.num2deg(x+1,y+1,zoom)
        self.xsize = 256 # TODO: no hard coded numbers
        self.ysize = 256

    def __make_url__(self, x, y, zoom):
        raise NotImplementedError()
        
    def deg2num(self, lat_deg, lon_deg, zoom):
        lat_rad = lat_deg * pi / 180.
        n = 2.0 ** zoom
        xtile = int((lon_deg + 180.0) / 360.0 * n)
        ytile = int((1.0 - np.arcsinh(np.tan(lat_rad)) / np.pi) / 2.0 * n)
        return (xtile, ytile)
    
    def num2deg(self, xtile, ytile, zoom):
    # This returns the NW-corner of the square. Use the function with xtile+1 and/or ytile+1 to get the other corners. With xtile+0.5 & ytile+0.5 it will return the center of the tile. 
        n = 2.0 ** zoom
        lon_deg = xtile / n * 360.0 - 180.0
        lat_rad = np.arctan(np.sinh(np.pi * (1 - 2 * ytile / n)))
        lat_deg = lat_rad * 180 / pi
        return (lat_deg, lon_deg)

class OSMTile(SlippyMapTile):
    def __make_url__(self, x, y, zoom):
        osm_url = "https://tile.openstreetmap.org/" + str(zoom) + "/" + str(x) + "/" + str(y) + ".png"
        return osm_url
    
class OSMScoutTile(SlippyMapTile):
    def __make_url__(self, x, y, zoom):
        osm_scout_url  = "http://localhost:8553/v1/tile?"
        osm_scout_url += "daylight=1"
        osm_scout_url += "&scale=1"
        osm_scout_url += "&z=" + str(zoom)
        osm_scout_url += "&x=" + str(x)
        osm_scout_url += "&y=" + str(y)
        return osm_scout_url
