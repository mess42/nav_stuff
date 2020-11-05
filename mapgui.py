#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, GLib, GdkPixbuf

import numpy as np
import datetime

import position_providers
import map_providers


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
        self.set_border_width(0)
        self.maximize()
        
        # Position provider
        self.position_provider = position_providers.PositionSimulation()
        valid_pos =  False
        while not valid_pos:
            valid_pos = self.position_provider.update_position()
            print("waiting for position fix ...")

        # Map provider
        self.map = map_providers.DebugMap()


        # Create Map Canvas Widget       
        self.map_canvas = Gtk.Overlay().new()

        # Create Map (background layer)
        tile_image = Gtk.Image()
        tile_image.connect("draw", self.draw_map)
        self.map_canvas.add(tile_image)
                
        # Create Markers (overlay on map)
        darea = Gtk.DrawingArea()
        darea.connect("draw", self.draw_map_overlay_markers)
        self.map_canvas.add_overlay(darea)

        # pack/grid widgets
        grid = Gtk.Grid()
        self.add(grid)
        grid.add(self.map_canvas)
        
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

        window_size = self.get_size()
        map_width  = window_size[0]
        map_height = window_size[1]
        marker_x = map_width // 2
        marker_y = map_height // 2

        ctx.set_source_rgb(0,0,0)
        ctx.arc(marker_x , marker_y, marker_radius_px, 0, 2*np.pi)
        ctx.fill()

        
        #marker_y, marker_x = self.map.angles_to_pxpos(self, lat_deg, lon_deg, tile_xsize_px, tile_ysize_px, tile_north_lat, tile_south_lat, tile_east_lon, tile_west_lon)
        #marker_x = int(np.round(self.tile.xsize * (marker_lon - self.tile.west_lon) / (self.tile.east_lon - self.tile.west_lon)))
        #marker_y = int(np.round(self.tile.ysize * (marker_lat - self.tile.north_lat) / (self.tile.south_lat - self.tile.north_lat)))
        
        #ctx.set_source_rgb(0,0,1)
        #ctx.arc(marker_x , marker_y, marker_radius_px, 0, 2*np.pi)
        #ctx.fill()
        
        ctx.set_source_rgb(0,1,0)
        ctx.move_to(10,50)
        ctx.show_text( "drawn at local time: " + str( datetime.datetime.now() ) )
        
    def draw_map(self, im, ctx):
        """
        @param im (Gtk image object)
        @param ctx (cairo context)
        """
        window_size = self.get_size()
        map_width  = window_size[0]
        map_height = window_size[1]
        
        arr = self.map.get_cropped_tile( 
                                    xsize_px = map_width, 
                                    ysize_px = map_height, 
                                    center_lat_deg = self.position_provider.latitude, 
                                    center_lon_deg = self.position_provider.longitude
                                    )
        pix = array_to_pixbuf(arr)
        im.set_from_pixbuf(pix)
        
        
if __name__ == "__main__":
    win = MapWindow()
    win.show_all()
    Gtk.main()