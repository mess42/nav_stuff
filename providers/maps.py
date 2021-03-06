#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
This file provides the map class.
The map is used create rendered images of a given cartogrpahic region.
At he moment, it contains 2D maps only.
In the future it could also contain a renderer of vector maps or 3D views.
"""
import hashlib

import numpy as np
from numpy import pi

from helpers import tile
import helpers.download

def get_mapping_of_names_to_classes():
    """
    @brief: Pointers to all classes that shall be usable.
    (no base classes)
    
    @return d (dict)
    """
    d = {"SlippyMap": SlippyMap,
         "DebugMap" : DebugMap,
        }
    return d
    

class SlippyMap(object):
    def __init__(self, url_template, min_zoom, max_zoom, default_zoom, map_copyright):
        self.cached_slippy_tiles = {}
        self.large_tile = tile.RasterTile(zoom=0)
        self.url_template = url_template
        self.min_zoom = min_zoom
        self.max_zoom = max_zoom
        self.current_zoom = default_zoom
        self.map_copyright = map_copyright
    
    @property
    def current_zoom(self):
        return self.__current_zoom

    @current_zoom.setter
    def current_zoom(self, new_zoom):
        new_zoom = min(new_zoom, self.max_zoom)
        new_zoom = max(new_zoom, self.min_zoom)
        self.__current_zoom = int(new_zoom)
    
    def zoom_in(self):
        self.current_zoom += 1
        
    def zoom_out(self):
        self.current_zoom -= 1
    
    def make_url(self, x, y, zoom):
        url = self.url_template.replace("{x}", str(x) )
        url =               url.replace("{y}", str(y) )
        url =               url.replace("{z}", str(zoom) )
        return url
        
    def deg2num(self, lat_deg, lon_deg, zoom):
        """
        https://wiki.openstreetmap.org/wiki/Slippy_map_tilenames#Python
        """
        lat_rad = lat_deg * pi / 180.
        n = 2.0 ** zoom
        xtile = int((lon_deg + 180.0) / 360.0 * n)
        ytile = int((1.0 - np.arcsinh(np.tan(lat_rad)) / np.pi) / 2.0 * n)
        return (xtile, ytile)
    
    def num2deg(self, xtile, ytile, zoom):
        """
        This returns the NW-corner of the square. Use the function with xtile+1 and/or ytile+1 to get the other corners. With xtile+0.5 & ytile+0.5 it will return the center of the tile. 
        https://wiki.openstreetmap.org/wiki/Slippy_map_tilenames#Python
        """
        n = 2.0 ** zoom
        lon_deg = xtile / n * 360.0 - 180.0
        lat_rad = np.arctan(np.sinh(np.pi * (1 - 2 * ytile / n)))
        lat_deg = lat_rad * 180 / pi
        return (lat_deg, lon_deg)
    
    def __download_slippy_tile_from_server__(self, x, y, zoom):
        """
        @brief: download a slippy map tile from the tile server and return it.
        
                This method uses bandwidth, so first check if there is a
                locally cached vesion of this tile before calling
                this method!
                
                This method does not store the resulting tile in the
                object's cache. Be sure to do so externally.
        
        @param x (int) slippy map tile number
        @param y (int)
        @param zoom (int)
        
        @return tile (dict)
        """
        url = self.make_url( x = x, y = y, zoom = zoom )
        north_lat, west_lon = self.num2deg(x  ,y  ,zoom)
        south_lat, east_lon = self.num2deg(x+1,y+1,zoom)
        arr = helpers.download.remote_png_to_numpy(url = url)
        ysize, xsize, c = np.shape(arr)
        
        slippy_tile = tile.RasterTile( raster_image   = arr ,
                                       angular_extent = {"north_lat": north_lat, "east_lon":  east_lon, "south_lat": south_lat, "west_lon":  west_lon },
                                       zoom           = zoom
                                     )
        return slippy_tile
    
    def get_slippy_tile(self,x,y,zoom):
        """
        @brief: get a slippy map tile.
        """
        if (zoom, x, y) not in self.cached_slippy_tiles:
            self.cached_slippy_tiles[(zoom, x, y)] = self.__download_slippy_tile_from_server__( x = x, y = y, zoom = zoom )
            #TODO: check if RAM is too full of cached tiles and remove some is necessary
        return self.cached_slippy_tiles[(zoom, x, y)]

    
    def get_rotated_cropped_tile(self, center_lat_deg, center_lon_deg, xsize_px, ysize_px, angle_rad=0 ):
        """
        @param center_lat_deg  (float)
        @param center_lon_deg  (float)
        @param xsize_px (int)
        @param ysize_px (int)
        
        @return im (3d numpy array of int)
        """
        
        # Can the large tile be cropped ?
        i_top, i_bottom, i_left, i_right = self.large_tile.get_cropping_indices_for_straight_enwrapping_of_rot_tile( center_lat_deg=center_lat_deg, center_lon_deg=center_lon_deg, cropped_xsize_px=xsize_px, cropped_ysize_px=ysize_px, angle_rad=angle_rad)

        cropping_indices_would_be_sane = self.large_tile.check_sanity_of_cropping_indices(i_top, i_bottom, i_left, i_right)

        large_tile_can_be_used = ( self.current_zoom == self.large_tile.zoom and cropping_indices_would_be_sane )

        # if large tile is unsuitable, make a new one
        if not large_tile_can_be_used:
            siz = 2 * max(xsize_px, ysize_px)
            self.large_tile = self.get_large_tile( lat_deg  = center_lat_deg, 
                                                   lon_deg  = center_lon_deg, 
                                                   zoom     = self.current_zoom, 
                                                   xsize_px = siz, 
                                                   ysize_px = siz 
                                                  )

        # now we can be sure that large tile fits the requested region, so let's crop
        if angle_rad == 0:
            cropped_tile = self.large_tile.get_cropped_tile_by_angles(
                                             center_lat_deg   = center_lat_deg, 
                                             center_lon_deg   = center_lon_deg, 
                                             cropped_xsize_px = xsize_px,
                                             cropped_ysize_px = ysize_px,
                                             )
        else:
            cropped_tile = self.large_tile.get_rotated_cropped_tile_by_angles(
                                             center_lat_deg   = center_lat_deg, 
                                             center_lon_deg   = center_lon_deg, 
                                             cropped_xsize_px = xsize_px,
                                             cropped_ysize_px = ysize_px,
                                             angle_rad        = angle_rad
                                             )
        
        return cropped_tile

    
    def get_large_tile(self, lat_deg, lon_deg, zoom, xsize_px , ysize_px ):
        """
        @brief: Build a large tile from which smaller raster images can be cut.
        """
        
        # Number of the center slippy map tile
        x_center, y_center = self.deg2num(lat_deg = lat_deg, lon_deg = lon_deg, zoom = zoom)
        
        # If not cached, get the center tile
        center_tile = self.get_slippy_tile(x = x_center, y = y_center, zoom = zoom)
        xsize_singletile = center_tile.xsize_px
        ysize_singletile = center_tile.ysize_px

        # Calculate how the large tile should look like:
        dx = int(np.ceil(.5 * ( xsize_px / xsize_singletile - 1 ) )) # tile index for stitching goes from -dx to dx
        dy = int(np.ceil(.5 * ( ysize_px / ysize_singletile - 1 ) ))
        xsize_large = (2*dx+1)*xsize_singletile
        ysize_large = (2*dy+1)*ysize_singletile
        north_lat, west_lon = self.num2deg(xtile = x_center-dx, ytile = y_center-dy, zoom=zoom)
        south_lat, east_lon = self.num2deg(xtile = x_center+dx+1, ytile = y_center+dy+1, zoom=zoom)
        
        # Stitch the large tile from small slippy map tiles
        image_large = np.zeros( (ysize_large, xsize_large,3) ,dtype=int)
        for ix in np.arange(2*dx+1)-dx:
            for iy in np.arange(2*dy+1)-dy:
                try:
                    current_tile = self.get_slippy_tile(x = x_center+ix, y = y_center+iy, zoom=zoom )
                except:
                    current_tile = np.zeros_like(center_tile)
                    print("Download failed. Drawing black tile.")
                    
                x0 = (ix+dx)   * xsize_singletile
                x1 = (ix+dx+1) * xsize_singletile
                y0 = (iy+dy)   * ysize_singletile
                y1 = (iy+dy+1) * ysize_singletile
                
                image_large[y0:y1,x0:x1] = current_tile.raster_image

        # Put all data in a tile
        large_tile = tile.RasterTile( zoom           = zoom,
                                      raster_image   = image_large,
                                      angular_extent = {"north_lat": north_lat, "east_lon":  east_lon, "south_lat": south_lat, "west_lon":  west_lon }
                                    )
        return large_tile
    
        
class DebugMap(SlippyMap):           
    def random_color(self,x,y,z):
        m = hashlib.md5()
        m.update(str(x).encode("ascii"))
        m.update(str(y).encode("ascii"))
        m.update(str(z).encode("ascii"))
        d = m.digest()
        r = d[0]
        g = d[1]
        b = d[2]
        return r,g,b
    
    def __download_slippy_tile_from_server__(self, x, y, zoom):
        """
        @brief: get a monochrome map tile in a random color.
        """
        north_lat, west_lon = self.num2deg(x  ,y  ,zoom)
        south_lat, east_lon = self.num2deg(x+1,y+1,zoom)
        xsize = 256
        ysize = 256
        arr   = np.zeros((ysize,xsize,3),dtype=int)
        rgb   = self.random_color(x,y,zoom)
        arr[:,:,0] = rgb[0]
        arr[:,:,1] = rgb[1]
        arr[:,:,2] = rgb[2]
        
        #make upper left corner white
        for i in np.arange(30):
            arr[i,:(30-i)] = 255
        
        slippy_tile = tile.RasterTile( zoom           = zoom,
                                       raster_image   = arr,
                                       angular_extent = {"north_lat": north_lat, "east_lon":  east_lon, "south_lat": south_lat, "west_lon":  west_lon }
                                     )
        return slippy_tile
