#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, GLib, GdkPixbuf


class MapLayerWidget(Gtk.Image):
    def update(self, cropped_tile):
        arr = cropped_tile.raster_image
        pix = self.array_to_pixbuf(arr)
        self.set_from_pixbuf(pix)
        
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
