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
        self.list_of_markers = [
                                FollowingMarker(drawer = Pin(fill_color=(0,1,0))),
                                FixedLatLonMarker(drawer = Pin(),
                                                  lat_deg = 50.97872,
                                                  lon_deg= 11.3319),
                                MetricScaleBarMarker(drawer = ScaleBar(), 
                                                  desired_size_px = 50,
                                                  xy_rel_to_window_size = [0,1], 
                                                  xy_abs_offset = [35,-25]),
                               ]
 
    def on_draw(self, da, ctx):
        """
        @brief: draw markers overlaid on the map.
        
        @param da (Gtk drawing area object)
        @param ctx (cairo context)
        """        
        for mark in self.list_of_markers:           
            mark.draw(ctx)
            
    def update(self, cropped_tile, latlon):
        """
        @brief: update the pixel positions of all markers
        """
        for mark in self.list_of_markers:           
            mark.update(cropped_tile, latlon)
        
        
class Marker(object):
    def __init__(self, drawer, **params):
        self.drawer = drawer
        self.x      = 0
        self.y      = 0
        
    def draw(self, ctx):
        self.drawer.draw(ctx, self.x, self.y)
    
    def update(self, cropped_tile, latlon):
        raise NotImplementedError("This is a base class")


class FixedXYMarker(Marker):
    def __init__(self, drawer, xy_rel_to_window_size = [0,0], xy_abs_offset = [0,0] ):
        """
        @brief: Marker with a fixed position compared to the window.
        
        Use for map-related GUI elements like scale bar or mini-compass.
        
        @param xy_rel_to_window_size (list of 2 float)
               [0,0] means top left
               [0,1] means bottom left
               [1,0] means top right
               [1,1] means bottom right
        @param xy_abs_offset (list of 2 float)
               Absolute offset in pixels.
               The offset is applied after calculating the relative location.
        """
        Marker.__init__(self, drawer)
        self.xy_rel_to_window_size = xy_rel_to_window_size 
        self.xy_abs_offset         = xy_abs_offset
    
    def update(self, cropped_tile, latlon):
        self.x = self.xy_rel_to_window_size[0] * cropped_tile.xsize_px + self.xy_abs_offset[0]
        self.y = self.xy_rel_to_window_size[1] * cropped_tile.ysize_px + self.xy_abs_offset[1]

    
class FixedLatLonMarker(Marker):
    def __init__(self, drawer, lat_deg, lon_deg):
        """
        @brief: Marker with a fixed position in latitude and longitude.
        
        Use for fixed objects like Destination, waypoints, or points of interest.
        """
        Marker.__init__(self, drawer)
        self.lat_deg = lat_deg
        self.lon_deg = lon_deg

    def update(self,cropped_tile, latlon):
        self.y, self.x = cropped_tile.angles_to_pxpos(lat_deg = self.lat_deg, lon_deg = self.lon_deg)

        
class FollowingMarker(Marker):
    """
    @brief: Marker that follows the ego position.
    """
    def update( self, cropped_tile, latlon):
        self.y, self.x = cropped_tile.angles_to_pxpos(lat_deg = latlon[0], lon_deg = latlon[1])


class MetricScaleBarMarker(FixedXYMarker):
    def __init__(self, drawer, xy_rel_to_window_size = [0,0], xy_abs_offset = [0,0], desired_size_px=50):
        if type(drawer) != ScaleBar:
            raise Exception("This marker type requires an instance of ScaleBar as drawer.")
        FixedXYMarker.__init__(self, drawer=drawer, xy_rel_to_window_size = xy_rel_to_window_size, xy_abs_offset=xy_abs_offset)
        self.desired_size_px   = desired_size_px
        self.candidate_sizes_m = np.array([10,20,50,100,200,500,1000,2000,5000,10000,20000,50000,100000,200000,500000,1000000])
        self.candidate_labels = []
        for i in range(len(self.candidate_sizes_m)):
            if self.candidate_sizes_m[i] < 1000:
                s = str(self.candidate_sizes_m[i]) + " m"
            else:
                s = str(int(self.candidate_sizes_m[i]//1000)) + " km"
            self.candidate_labels.append(s)

    def update(self, cropped_tile, latlon):
        candidate_sizes_px = self.candidate_sizes_m / cropped_tile.get_scale_in_m_per_px()
        
        # Find the scale size closest to the desired one
        i = np.argmin(abs(candidate_sizes_px - self.desired_size_px))
        
        self.drawer.xsize = int(round(candidate_sizes_px[i]))
        self.drawer.ysize = 15
        self.drawer.label = self.candidate_labels[i]
        
        self.x = self.xy_rel_to_window_size[0] * cropped_tile.xsize_px + self.xy_abs_offset[0]
        self.y = self.xy_rel_to_window_size[1] * cropped_tile.ysize_px + self.xy_abs_offset[1]


class Pin(object):
    def __init__(self, 
                 width=20, 
                 height = 30, 
                 fill_color=(1,0,0), 
                 border_color=(0,0,0),
                 dot_fill_color = (1,1,1),
                 dot_border_color = (0,0,0)
                 ):
        """
        @brief: stores the geometry and draws a marker pin.
        """
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
        """
        @brief: draw the pin.
        
        @param ctx (Cairo context)
        @param x (int) position of the tip apex in px
        @param y (int) position of the tip apex in px
        """
        # Outline contour
        ctx.move_to(x    , y)
        ctx.line_to(x+self.dx , y+self.dy)
        ctx.arc(    x    , y-self.t, self.r, self.phi0, self.phi1)
        ctx.line_to(x    , y)
        
        # fill and stroke the outline
        ctx.set_source_rgb(*self.border_color)
        ctx.stroke_preserve()
        ctx.set_source_rgb(*self.fill_color)
        ctx.fill()

        # the central dot
        ctx.arc(    x , y-self.t, .4*self.r, 0, 2*np.pi)
        
        # fill and stroke the dot
        ctx.set_source_rgb(*self.dot_border_color)
        ctx.stroke_preserve()
        ctx.set_source_rgb(*self.dot_fill_color)
        ctx.fill()


class ScaleBar(object):
    def __init__(self, size_px=50, label="1 arbitrary unit", color=(0,0,0)):
        self.color =color
        self.xsize = size_px
        self.ysize = 0.2 * size_px
        self.label = label
        
    def draw(self, ctx, x, y):
        ctx.set_source_rgb(*self.color)
        ctx.rectangle(x,y, self.xsize, self.ysize)
        ctx.fill()
        ctx.move_to( x+self.xsize+5, y+self.ysize-1 )
        ctx.show_text( self.label )
