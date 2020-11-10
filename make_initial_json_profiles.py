#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Nov 10 19:33:22 2020

@author: foerster
"""

import json



# people who like braces also liked: Lisp
d = {"MapProviders": {
        "OpenStreetMap":
            {"class_name":"SlippyMap",
             "parameters":{"url_template":"https://tile.openstreetmap.org/{z}/{x}/{y}.png"} 
            },
         "OpenTopoMap":
            {"class_name":"SlippyMap",
             "parameters":{"url_template":"https://tile.opentopomap.org/{z}/{x}/{y}.png"} 
            },
         "OSMScout":
            {"class_name":"SlippyMap",
             "parameters":{"url_template":"http://localhost:8553/v1/tile?daylight=1&scale=1&z={z}&x={x}&y={y}"} 
            },
        },
    "PositionProviders": {
        "SerialNMEA":
            {"class_name":"PositionSerialNMEA",
             "parameters":{"serial_port": "/dev/ttyUSB1"}
            },
         "GeoClue":
            {"class_name":"PositionGeoClue",
             "parameters":{}
            },             
         "PositionSimulation":
            {"class_name":"PositionSimulation",
             "parameters":{}
            },
        },
    }

f = open("profiles.json","w")
json.dump(d,f)
f.close()



