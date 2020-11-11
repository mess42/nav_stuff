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
        """
        @brief: update the pixel positions of all markers
        """
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
    def __init__(self, 
                 width=20, 
                 height = 30, 
                 fill_color=(1,0,0), 
                 border_color=(0,0,0),
                 dot_fill_color = (1,1,1),
                 dot_border_color = (0,0,0)
                 ):
        
        # Color stuff
        self.fill_color       = fill_color
        self.border_color     = border_color
        self.dot_fill_color   = dot_fill_color
        self.dot_border_color = dot_border_color

        # Geometry stuff
        self.r = int(round(0.5*width)) # radius in px
        self.t = int(round(height-self.r)) # distance from circle center to tip        
        sina = self.r / self.t
        cosa = np.sqrt(1-sina**2)
        self.phi0 = np.pi- np.arcsin(sina) # start angle of the upper arc
        self.phi1 = np.arcsin(sina)        # stop angle of the upper arc
        self.dy = - self.t + self.r * sina # y pos of the interface arc to tip
        self.dx = -self.r*cosa             # x pos of the interface arc to tip
        
    def draw(self, ctx, x, y):      
        ctx.move_to(x    , y)
        ctx.line_to(x+self.dx , y+self.dy)
        ctx.arc(    x    , y-self.t, self.r, self.phi0, self.phi1)
        ctx.line_to(x    , y)
        ctx.set_source_rgb(*self.border_color)
        ctx.stroke_preserve()
        ctx.set_source_rgb(*self.fill_color)
        ctx.fill()

        ctx.arc(    x , y-self.t, .4*self.r, 0, 2*np.pi)
        ctx.set_source_rgb(*self.dot_border_color)
        ctx.stroke_preserve()
        ctx.set_source_rgb(*self.dot_fill_color)
        ctx.fill()
