#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, GLib, GdkPixbuf

import datetime
import numpy as np

class MarkerLayerWidget(Gtk.DrawingArea):
    
    def __init__(self):       
        Gtk.DrawingArea.__init__(self)
        self.connect("draw", self.on_draw)
                
        #TODO: make it controllable which markers are included in the list
        #TODO: ego marker position should be based on angles, and not hard code the map center
        self.list_of_markers = [
                                FixedXYMarker(drawer = Pin(), 
                                              xy_rel_to_window_size = [0.5,0.5])
                               ]
 
    def on_draw(self, da, ctx):
        """
        @brief: draw markers overlaid on the map.
        
        @param da (Gtk drawing area object)
        @param ctx (cairo context)
        """        
        for mark in self.list_of_markers:           
            mark.draw(ctx)
            
        ctx.set_source_rgb(0,1,0)
        ctx.move_to(10,50)
        ctx.show_text( "drawn at local time: " + str( datetime.datetime.now() ) )

    def update(self, cropped_tile):
        for mark in self.list_of_markers:           
            mark.update(cropped_tile)
        
        
class Marker(object):
    def __init__(self, drawer, **params):
        self.drawer = drawer
        self.x      = 0
        self.y      = 0
        raise NotImplementedError()
        
    def draw(self, ctx):
        self.drawer.draw(ctx, self.x, self.y)
    
    def update(self, cropped_tile):
        raise NotImplementedError()

class FixedXYMarker(Marker):
    def __init__(self, drawer, xy_rel_to_window_size = [0,0], xy_abs_offset = [0,0] ):
        """
        @brief: Marker with a fixed position compared to the window.
        
        Use for map-related GUI elements like scale bar or mini-compass.
        """
        self.drawer                = drawer
        self.xy_rel_to_window_size = xy_rel_to_window_size 
        self.xy_abs_offset         = xy_abs_offset
        self.x = 0
        self.y = 0
    
    def update(self, cropped_tile):
        self.x = self.xy_rel_to_window_size[0] * cropped_tile.xsize_px + self.xy_abs_offset[0]
        self.y = self.xy_rel_to_window_size[1] * cropped_tile.ysize_px + self.xy_abs_offset[1]
    
class FixedLatLonMarker(Marker):
    def __init__(self, drawer, lat=0, lon=0):
        """
        @brief: Marker with a fixed position in latitude or longitude.
        
        Use for fixed objects like Destination, waypoints, or points of interest.
        """
        raise NotImplementedError()
        
class FollowingMarker(Marker):
    def __init__(self, drawer, init_lat=0, init_lon=0):
        """
        @brief: Marker following the ego position.
        """
        raise NotImplementedError()


class Pin(object):
    def __init__(self):
        pass
        
    def draw(self, ctx, x, y):
        r = 10 # radius in px
        h = 2*r       # distance from circle center to tip
        sina = r / h
        alpha = np.arcsin(sina)
        cosa = np.sqrt(1-sina**2)
        dy = - h + r * sina
        dx = -r*cosa
        
        ctx.set_source_rgb(0,0,1)
        ctx.move_to(x    , y)
        ctx.line_to(x+dx , y+dy)
        ctx.arc(    x    , y-h, r, np.pi-alpha,alpha)
        ctx.line_to(x    , y)
        ctx.stroke_preserve()

        ctx.set_source_rgb(1,0,0)
        ctx.fill()

        ctx.set_source_rgb(0,1,0)
        ctx.arc(    x , y-h, .4*r, 0, 2*np.pi)
        ctx.fill()