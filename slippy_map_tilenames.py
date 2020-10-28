#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
https://wiki.openstreetmap.org/wiki/Slippy_map_tilenames#Python
"""

import math
def deg2num(lat_deg, lon_deg, zoom):
  lat_rad = math.radians(lat_deg)
  n = 2.0 ** zoom
  xtile = int((lon_deg + 180.0) / 360.0 * n)
  ytile = int((1.0 - math.asinh(math.tan(lat_rad)) / math.pi) / 2.0 * n)
  return (xtile, ytile)

def num2deg(xtile, ytile, zoom):
  n = 2.0 ** zoom
  lon_deg = xtile / n * 360.0 - 180.0
  lat_rad = math.atan(math.sinh(math.pi * (1 - 2 * ytile / n)))
  lat_deg = math.degrees(lat_rad)
  return (lat_deg, lon_deg)

# This returns the NW-corner of the square. Use the function with xtile+1 and/or ytile+1 to get the other corners. With xtile+0.5 & ytile+0.5 it will return the center of the tile. 
  
zoom = 18
lat = 50.90838
lon = 11.56821

x,y = deg2num(lat_deg=lat, lon_deg=lon, zoom=zoom)

osm_url = "https://tile.openstreetmap.org/" + str(zoom) + "/" + str(x) + "/" + str(y) + ".png"

osm_scout_url = "http://localhost:8553/v1/tile?z=" + str(zoom) + "&x=" + str(x) + "&y=" + str(y)

page  = "<img src=\"" + osm_url + "\">"
page += "<br>osm<br><br>"
page += "<img src=\"" + osm_scout_url + "\">"
page += "<br>osm scout<br><br>"

f = open("tiles.html","w")
f.write(page)
f.close()