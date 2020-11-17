#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
This file contains the Tile class.
"""
import numpy as np

class RasterTile(object):
    def __init__(self, 
                 zoom,
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
        self.zoom          = zoom
        self.raster_image  = raster_image
        self.north_lat     = angular_extent["north_lat"]
        self.south_lat     = angular_extent["south_lat"]
        self.east_lon      = angular_extent["east_lon"]
        self.west_lon      = angular_extent["west_lon"]
        shap               = np.shape(raster_image)
        self.ysize_px      = shap[0]
        self.xsize_px      = shap[1]
        
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

    def pxpos_to_angles(self, iy, ix):
        """
        @brief: get angles for given get pixel coordinates.
        
        self.west_lon is the coordinate of the pixel ix=0.
        self.east_lon is the coordinate of the next tile pixel ix=0
        or this tile ix = self.ysize_px (index out of bounds). 
        It cannot be reached with an index inside this tile.
        
        In close analogy, iy=0 represents self.north_lat of this tile,
        and self.south_lat is outside of this tile.
        
        @param iy (int)
        @param ix (int)

        @return lat_deg (float)
        @return lon_deg (float)
        """
        lat_deg = self.north_lat + iy / self.ysize_px * (self.south_lat - self.north_lat) 
        lon_deg = self.west_lon  + ix / self.xsize_px * (self.east_lon  - self.west_lon )
        return lat_deg, lon_deg

    def get_cropping_indices(self, center_lat_deg, center_lon_deg, cropped_xsize_px, cropped_ysize_px):
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

    def check_sanity_of_cropping_indices(self, i_top, i_bottom, i_left, i_right):
        """
        @brief: Is it possible to crop without "out of bounds" errors ?
        
        @param i_top    (int)
        @param i_bottom (int)
        @param i_left   (int)
        @param i_right  (int)
        
        @return is_sane (bool)
        """
        is_sane = (     i_top    >= 0 
                    and i_bottom <  self.ysize_px
                    and i_top    <  i_bottom
                    and i_left   >= 0 
                    and i_right  <  self.xsize_px
                    and i_left   <  i_right
                   )
        return is_sane
    
    def check_sanity_of_cropping_angles(self, center_lat_deg, center_lon_deg, cropped_xsize_px, cropped_ysize_px):
        i_top, i_bottom, i_left, i_right = self.get_cropping_indices( center_lat_deg   = center_lat_deg, center_lon_deg   = center_lon_deg, cropped_xsize_px = cropped_xsize_px, cropped_ysize_px = cropped_ysize_px )
        is_sane                          = self.check_sanity_of_cropping_indices( i_top, i_bottom, i_left, i_right)
        return is_sane
 
    def get_cropped_tile_by_indices(self, i_top, i_bottom, i_left, i_right):
        if not self.check_sanity_of_cropping_indices(i_top, i_bottom, i_left, i_right):
            raise Exception("Cropping indices are corrupt.")
        cropped_im          = self.raster_image[i_top:i_bottom,i_left:i_right]
        north_lat, west_lon = self.pxpos_to_angles(iy=i_top,    ix=i_left )
        south_lat, east_lon = self.pxpos_to_angles(iy=i_bottom, ix=i_right)
        
        cropped_tile = RasterTile( zoom           = self.zoom, 
                                   raster_image   = cropped_im,
                                   angular_extent = {"north_lat": north_lat, "south_lat": south_lat, "east_lon":  east_lon, "west_lon":  west_lon },
                                 )
        return cropped_tile

    def get_cropped_tile_by_angles(self, center_lat_deg, center_lon_deg, cropped_xsize_px, cropped_ysize_px):
        i_top, i_bottom, i_left, i_right = self.get_cropping_indices( center_lat_deg, center_lon_deg, cropped_xsize_px, cropped_ysize_px)
        cropped_tile = self.get_cropped_tile_by_indices( i_top=i_top, i_bottom=i_bottom, i_left=i_left, i_right=i_right)
        return cropped_tile

    def get_scale_in_m_per_px(self):
        """
        @brief: Get a map scale.
        
        Approximation: 1 degree latitude is 111 km.
        (Actually, the earth is elliptical, and an
        equatorial degree latitude corresponds to 110574 m, whereas a
        polar degree latitude corresponds to 111694 m,
        so this result is off by up to 0.5%)
        
        In the Mercator projection, the longitudinal magnification
        varies greatly with latitude, so a scale may be inappropriate
        for tiles with a large lateral span.
        
        @return scale (float)
        """
        total_ns_extent_in_m = 111000 * (self.north_lat - self.south_lat)
        return total_ns_extent_in_m / self.ysize_px
        