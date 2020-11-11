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
        self.list_of_markers = []
 
    def on_draw(self, da, ctx):
        """
        @brief: draw markers overlaid on the map.
        
        @param da (Gtk drawing area object)
        @param ctx (cairo context)
        """
        r = 10 # radius in px
        h = 2*r       # distance from circle center to tip
        sina = r / h
        alpha = np.arcsin(sina)
        cosa = np.sqrt(1-sina**2)
        y = - h + r * sina
        x = -r*cosa
        
        for mark in self.list_of_markers:           
            #TODO: allow different marker styles (dot, cross, arrow)
            """
            ctx.set_source_rgb(*mark["color"])
            ctx.arc(mark["x"] , mark["y"], 0.5*w, 0, 2*np.pi)
            ctx.fill()
            """
            ctx.set_source_rgb(0,0,1)
            ctx.move_to(mark["x"] , mark["y"])
            ctx.line_to(mark["x"]+x , mark["y"]+y)
            ctx.arc(    mark["x"] , mark["y"]-h, r, np.pi-alpha,alpha)
            ctx.line_to(mark["x"] , mark["y"])
            ctx.stroke_preserve()

            ctx.set_source_rgb(1,0,0)
            ctx.fill()

            ctx.set_source_rgb(0,1,0)
            ctx.arc(    mark["x"] , mark["y"]-h, .4*r, 0, 2*np.pi)
            ctx.fill()
        
        ctx.set_source_rgb(0,1,0)
        ctx.move_to(10,50)
        ctx.show_text( "drawn at local time: " + str( datetime.datetime.now() ) )

    def update(self, cropped_tile):
        #TODO: make it controllable which markers are included in the list
        #TODO: ego marker position should be based on angles, and not hard code the map center
        self.list_of_markers = [
                            {"x": cropped_tile.xsize_px//2, "y": cropped_tile.ysize_px//2, "color": (0,0,0) },
                          ]
        #y,x = cropped_tile.angles_to_pxpos(lat_deg, lon_deg)