#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, GLib, GdkPixbuf

from helpers.tile import RasterTile
import numpy as np

class MapLayerWidget(Gtk.Image):
    def __init__(self, hide_map = False):
        Gtk.Image.__init__(self)
        self.__hide_map = hide_map
    
    def update(self, cropped_tile):
        if not self.hide_map:
            arr = cropped_tile.raster_image
            pix = self.array_to_pixbuf(arr)
            self.set_from_pixbuf(pix)
            self.set_size_request(1,1)

    @property 
    def hide_map(self):
        return self.__hide_map
        
    @hide_map.setter
    def hide_map(self, new_value):
        self.update( cropped_tile = RasterTile(zoom=0))
        self.__hide_map = new_value
        
    def array_to_pixbuf(self, arr):
        """ 
        convert from numpy array to GdkPixbuf 
        """
        z     = arr.astype('uint8')
        h,w,c = z.shape
        assert c == 3 or c == 4
        pix = None
        if hasattr(GdkPixbuf.Pixbuf,'new_from_bytes'):
            Z = GLib.Bytes.new(z.tobytes())
            pix = GdkPixbuf.Pixbuf.new_from_bytes(Z, GdkPixbuf.Colorspace.RGB, c==4, 8, w, h, w*c)
        else:
            pix = GdkPixbuf.Pixbuf.new_from_data(z.tobytes(),  GdkPixbuf.Colorspace.RGB, c==4, 8, w, h, w*c, None, None)
        return pix
