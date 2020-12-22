#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
from polyline.polyline.codec import PolylineCodec

filename = "valhalla_result.json"
f = open(filename,"r")
dic = json.load(f)
f.close()

shape = dic["trip"]["legs"][0]["shape"]

#print(dic["trip"]["legs"][0]["maneuvers"])


decoder = PolylineCodec()

print( decoder.decode( shape, precision=6) )