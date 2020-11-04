#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
This file contains the Tile class.
"""
import numpy as np

class RasterTile(object):
    def __init__(self, zoom,
                       raster_image   = np.array([[[0,0,0]]]),
                       angular_extent = {"north_lat": 1E-9, 
                                         "south_lat": 0, 
                                         "east_lon":  0,
                                         "west_lon":  1E-9
                                         }
                 ):
        """
        @brief Data container for a raster tile.
        
        @param raster_image (3d numpy array of int)
                            Indices are [ y, x, colour_channel ]
        @param angular_extent (dict)
                            north, south, east and west 
                            latitude and longitude in deg.
        """
        self.zoom         = zoom
        self.raster_image = raster_image
        self.north_lat    = angular_extent["north_lat"]
        self.south_lat    = angular_extent["south_lat"]
        self.east_lon     = angular_extent["east_lon"]
        self.west_lon     = angular_extent["west_lon"]
        shap              = np.shape(raster_image)
        self.ysize_px     = shap[0]
        self.xsize_px     = shap[1]
