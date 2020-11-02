#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, GLib, GdkPixbuf

import numpy as np
import datetime

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

class MapWindow(Gtk.Window):
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
            print("waiting for position fix ...")
        self.tile = tile_providers.OSMScoutTile(lat_deg = self.position_provider.latitude, 
                                      lon_deg = self.position_provider.longitude
                                      )

        # Create widgets
        # Create Map (background layer)
        self.canvas = Gtk.Overlay().new()
        tile_image = Gtk.Image()
        arr = download_helpers.remote_png_to_numpy(url = self.tile.url)
        pix = array_to_pixbuf(arr)
        tile_image.set_from_pixbuf(pix)
        self.canvas.add(tile_image)
                
        # Create Markers (overlay on map)
        darea = Gtk.DrawingArea()
        darea.connect("draw", self.draw_map_overlay_markers)
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
    
    def on_destroy(self, object_to_destroy):
        """
        Actions to be performed before destroying this application.
        """
        self.position_provider.disconnect()
        print("Position provider disconnected.")
        Gtk.main_quit(object_to_destroy)
        
    
    def draw_map_overlay_markers(self, da, ctx):
        """
        @param da (Gtk drawing area object)
        @param ctx (cairo context)
        """
        marker_lat = self.position_provider.latitude
        marker_lon = self.position_provider.longitude
        marker_radius_px = 10
        
        marker_x = int(np.round(self.tile.xsize * (marker_lon - self.tile.west_lon) / (self.tile.east_lon - self.tile.west_lon)))
        marker_y = int(np.round(self.tile.ysize * (marker_lat - self.tile.north_lat) / (self.tile.south_lat - self.tile.north_lat)))
        
        ctx.set_source_rgb(0,0,1)
        ctx.arc(marker_x , marker_y, marker_radius_px, 0, 2*np.pi)
        ctx.fill()
        
        ctx.set_source_rgb(1,0,0)
        ctx.move_to(50,50)
        ctx.show_text( "drawn at local time: " + str( datetime.datetime.now() ) )
        
        
        
        
if __name__ == "__main__":
    win = MapWindow()
    win.show_all()
    Gtk.main()