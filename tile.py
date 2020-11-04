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
        
    def angles_to_pxpos(self, lat_deg, lon_deg):
        """
        @brief: get pixel coordinates for given angles.

        No sanity check is performed.
        The indices returned may be outside the tile.
        
        @param lat_deg (float)
        @param lon_deg (float)

        @return iy (int)
        @return ix (int)
        """
        ix = int(np.round(self.xsize_px * (lon_deg - self.west_lon) / (self.east_lon - self.west_lon)))
        iy = int(np.round(self.ysize_px * (lat_deg - self.north_lat) / (self.south_lat - self.north_lat)))
        return iy, ix

    def get_cropping_recipe(self, center_lat_deg, center_lon_deg, cropped_xsize_px, cropped_ysize_px):
        """
        @brief: get pixel coordinates to cut a tile.
        
        No sanity check is performed.
        The indices returned may be outside the tile.
        
        @param center_lat_deg (float)
        @param center_lon_deg (float)
        @param cropped_xsize_px (int)
        @param cropped_ysize_px (int)
        
        @return i_top    (int)
        @return i_bottom (int)
        @return i_left   (int)
        @return i_right  (int)
        """
        iy_center, ix_center = self.angles_to_pxpos( lat_deg = center_lat_deg, lon_deg = center_lon_deg )    
        
        i_left   = ix_center - cropped_xsize_px // 2
        i_right  = i_left    + cropped_xsize_px
        i_top    = iy_center - cropped_ysize_px // 2
        i_bottom = i_top     + cropped_ysize_px
        
        return i_top, i_bottom, i_left, i_right
