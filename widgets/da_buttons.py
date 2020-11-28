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
    def __init__(self, size=32):
        DrawingAreaButton.__init__(self, size=size)
        
        self.size=size
        
        # left half
        self.xl  = size * np.array([.5,.5, .2,.5])
        self.yl  = size * np.array([ 0,.8,.95, 0])
        
        # right half
        self.xr  = size * np.array([.5, .8,.5,.5])
        self.yr  = size * np.array([ 0,.95,.8, 0])
        
        # total outline
        self.x  = size * np.array([.5, .8,.5, .2,.5])
        self.y  = size * np.array([ 0,.95,.8,.95, 0])
        
    def on_draw(self, da, ctx):
        ctx.set_source_rgba(1,1,1,.7)
        ctx.rectangle(0,0,self.size,self.size)
        ctx.fill()

        ctx.set_source_rgb(1,1,1)
        self.polygon(ctx, self.xl, self.yl)
        ctx.fill()
        
        ctx.set_source_rgb(0,0,0)
        self.polygon(ctx, self.xr, self.yr)
        ctx.fill()
        self.polygon(ctx, self.x, self.y)
        ctx.stroke()


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