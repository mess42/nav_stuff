#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import numpy as np

def distance_to_rounded_textblocks(distance_in_m):
    out = {}
    if distance_in_m < 20:
        out["distance_preposition"] = "in"
        d = int(np.round(distance_in_m,0))
        out["distance"] = str( d )
        out["distance_unit"] = "meters"
        out["distance_unit_abbrev"] = "m"
        if d == 1:
            out["distance_unit"] = "meter"                      
    elif distance_in_m < 200:
        out["distance_preposition"] = "in"
        out["distance"] = str( int(np.round(distance_in_m,-1)) )
        out["distance_unit"] = "meters"
        out["distance_unit_abbrev"] = "m"
    elif distance_in_m < 1000:
        out["distance_preposition"] = "in"
        out["distance"] = str( int(np.round(distance_in_m,-2)) )
        out["distance_unit"] = "meters"
        out["distance_unit_abbrev"] = "m"
    elif distance_in_m < 20000:
        out["distance_preposition"] = "in"
        d = np.round(distance_in_m/1000,1)
        out["distance"] = str( d )
        out["distance_unit"] = "kilometers"
        out["distance_unit_abbrev"] = "km"
        if d == 1:
            out["distance_unit"] = "kilometer"                      
    elif distance_in_m < 100000:
        out["distance_preposition"] = "in"
        out["distance"] = str( int(np.round(distance_in_m/1000)) )
        out["distance_unit"] = "kilometers"
        out["distance_unit_abbrev"] = "km"
    else:
        out["distance_preposition"] = "in"
        out["distance"] = str( int(np.round(distance_in_m/1000,-1)) )
        out["distance_unit"] = "kilometers"
        out["distance_unit_abbrev"] = "km"
    
    return out

