#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, GLib, GdkPixbuf

import numpy as np

import position_providers
import tile_providers
import download_helpers


def array_to_pixbuf(arr):
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

class ButtonWindow(Gtk.Window):
    def __init__(self):
        
        # Global window initialisation
        Gtk.Window.__init__(self)
        self.connect("destroy", self.on_destroy)
        self.set_title("Map Demo")
        #self.set_default_size(390, 240)
        self.set_border_width(10)
        
        # Position provider
        self.position_provider = position_providers.PositionSimulation()
        
        # Tile provider
        valid_pos =  False
        while not valid_pos:
            valid_pos = self.position_provider.update_position()
            print("waiting for GPS fix ...")

        self.tile = tile_providers.OSMScoutTile(lat_deg = self.position_provider.latitude, 
                                      lon_deg = self.position_provider.longitude
                                      )

        # Create widgets
        self.canvas = Gtk.Overlay().new()

        tile_image = Gtk.Image()

        arr = download_helpers.remote_png_to_numpy(url = self.tile.url)
        pix = array_to_pixbuf(arr)
    
        tile_image.set_from_pixbuf(pix)
        self.canvas.add(tile_image)
                
        darea = Gtk.DrawingArea()
        darea.connect("draw", self.on_draw)
        self.canvas.add_overlay(darea)

        # pack/grid widgets
        grid = Gtk.Grid()
        self.add(grid)
        grid.add(self.canvas)
        
        #self.timeout_id = GLib.timeout_add(500, self.on_timeout, None)
    
    #def on_timeout(self, data):
    #    print("bla")
    #    repeat = True
    #    return repeat
    
    def on_destroy(self):
        self.position_provider.disconnect()
        print("Position provider disconnected.")
        Gtk.main_quit()
        print("Let's see whether this is displayed.")
        
    
    def on_draw(self, da, ctx):

        marker_lat = self.position_provider.latitude
        marker_lon = self.position_provider.longitude
        marker_radius_px = 10
        
        marker_x = int(np.round(self.tile.xsize * (marker_lon - self.tile.west_lon) / (self.tile.east_lon - self.tile.west_lon)))
        marker_y = int(np.round(self.tile.ysize * (marker_lat - self.tile.north_lat) / (self.tile.south_lat - self.tile.north_lat)))
        
        ctx.set_source_rgb(0,0,1)
        ctx.arc(marker_x , marker_y, marker_radius_px, 0, 2*np.pi)
        ctx.fill()
        
        
        
        
if __name__ == "__main__":
    win = ButtonWindow()
    win.show_all()
    Gtk.main()