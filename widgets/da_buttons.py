#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gdk, GLib

import numpy as np

class DrawingAreaButton(Gtk.DrawingArea):
    def __init__(self, size=32):
        Gtk.DrawingArea.__init__(self)
        self.add_events(Gdk.EventMask.BUTTON_PRESS_MASK)
        self.connect("draw", self.on_draw)
        self.set_size_request(size,size)
        
    def polygon(self,ctx,x,y):
        ctx.move_to(x[0], y[0])
        for i in np.arange(len(x)-1)+1:
            ctx.line_to(x[i],y[i])
        
               
class NorthArrow(DrawingAreaButton):
    def __init__(self, north_bearing_deg = 0, size=32):
        DrawingAreaButton.__init__(self, size=size)
        
        self.size=size
        self.update( north_bearing_deg=north_bearing_deg )
        
    def update(self, north_bearing_deg):
        bear_rad = north_bearing_deg * np.pi/180.

        # right half        
        dxr = np.array([   0, .3, 0,   0])
        dyr = np.array([ -.45,.4,.3, -.45])        
        self.xr  = self.size * (dxr*np.cos(bear_rad) - dyr*np.sin(bear_rad) + .5)
        self.yr  = self.size * (dxr*np.sin(bear_rad) + dyr*np.cos(bear_rad) + .5)
        
        # total outline
        dx = np.array([   0, .3, 0, -.3,   0])
        dy = np.array([ -.45,.4,.3, .4, -.45])
        self.x  = self.size * (dx*np.cos(bear_rad) - dy*np.sin(bear_rad) + .5)
        self.y  = self.size * (dx*np.sin(bear_rad) + dy*np.cos(bear_rad) + .5)
        
    def on_draw(self, da, ctx):
        ctx.set_source_rgba(1,1,1,.7)
        ctx.rectangle(0,0,self.size,self.size)
        ctx.fill()

        self.polygon(ctx, self.x, self.y)
        ctx.set_source_rgb(1,1,1)
        ctx.fill_preserve()
        ctx.set_source_rgb(0,0,0)        
        ctx.stroke()
        self.polygon(ctx, self.xr, self.yr)
        ctx.fill()



class ZoomOut(DrawingAreaButton):
    def __init__(self, size=32):
        DrawingAreaButton.__init__(self, size=size)
        
        self.size=size
        w = .08 # bar width
        e = .18  # distance from edge
        
        self.y  = size * np.array([.5+w, .5+w, .5-w, .5-w, .5+w])
        self.x  = size * np.array([   e,  1-e,  1-e,    e,    e])
        
    def on_draw(self, da, ctx):
        ctx.set_source_rgba(1,1,1,.7)
        ctx.rectangle(0,0,self.size,self.size)
        ctx.fill()
        
        ctx.set_source_rgb(0,0,0)
        self.polygon(ctx, self.x, self.y)
        ctx.fill()


class ZoomIn(DrawingAreaButton):
    def __init__(self, size=32):
        DrawingAreaButton.__init__(self, size=size)
        
        self.size=size
        w = .08 # bar width
        e = .18  # distance from edge
        
        self.y  = size * np.array([.5-w, .5-w,    e,    e, .5-w, .5-w, .5+w, .5+w,  1-e,  1-e, .5+w, .5+w, .5-w])
        self.x  = size * np.array([   e, .5-w, .5-w, .5+w, .5+w,  1-e,  1-e, .5+w, .5+w, .5-w, .5-w,    e,    e])
        
    def on_draw(self, da, ctx):
        ctx.set_source_rgba(1,1,1,.7)
        ctx.rectangle(0,0,self.size,self.size)
        ctx.fill()
        
        ctx.set_source_rgb(0,0,0)
        self.polygon(ctx, self.x, self.y)
        ctx.fill()

class Settings(DrawingAreaButton):
    def __init__(self, size=32):
        DrawingAreaButton.__init__(self, size=size)
        
        self.size=size
        w = .05 # bar width
        e = .12  # distance from edge
        
        self.y2  = size * np.array([.5+w, .5+w, .5-w, .5-w, .5+w])
        self.x   = size * np.array([   e,  1-e,  1-e,    e,    e])
        
        self.y1 = self.y2 - .25 * size
        self.y3 = self.y2 + .25 * size
        
        
    def on_draw(self, da, ctx):
        ctx.set_source_rgba(1,1,1,.7)
        ctx.rectangle(0,0,self.size,self.size)
        ctx.fill()
        
        ctx.set_source_rgb(0,0,0)
        self.polygon(ctx, self.x, self.y1)
        ctx.fill()
        self.polygon(ctx, self.x, self.y2)
        ctx.fill()
        self.polygon(ctx, self.x, self.y3)
        ctx.fill()