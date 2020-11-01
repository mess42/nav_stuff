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
lat = 50.97872
lon = 11.3319

x,y = deg2num(lat_deg=lat, lon_deg=lon, zoom=zoom)

print("desired_lat        ", lat)
print("tile north edge lat", num2deg(x,y,zoom)[0])
print("tile south edge lat", num2deg(x,y+1,zoom)[0])

print("desired_lon        ", lon)
print("tile west  edge lon", num2deg(x,y,zoom)[1])
print("tile east  edge lon", num2deg(x+1,y,zoom)[1])

osm_url = "https://tile.openstreetmap.org/" + str(zoom) + "/" + str(x) + "/" + str(y) + ".png"

osm_scout_url  = "http://localhost:8553/v1/tile?"
# style={style}
osm_scout_url += "daylight=1"
osm_scout_url += "&shift=1"
osm_scout_url += "&scale=2"
osm_scout_url += "&z=" + str(zoom)
osm_scout_url += "&x=" + str(x)
osm_scout_url += "&y=" + str(y)


page  = "<img src=\"" + osm_url + "\">"
page += "<br>osm<br><br>"
page += "<img src=\"" + osm_scout_url + "\">"
page += "<br>osm scout<br><br>"

f = open("tiles.html","w")
f.write(page)
f.close()