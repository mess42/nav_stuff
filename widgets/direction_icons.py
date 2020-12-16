#!/usr/bin/env python3
# -*- coding: utf-8 -*-


from numpy import pi
import numpy as np
from widgets.da_buttons import DrawingAreaButton

class DirectionIcon(DrawingAreaButton):
    def __init__(self, in_bearing_deg=0, out_bearing_deg=0, bearings_deg=[], size=32, left_driving=False):
        pass
    
    def on_draw(self, da, ctx):
        raise NotImplementedError("This is a base class.")
    
    def make_street_polygon(self, bearings_rad, size):
        N = len(bearings_rad)
        w = .1 # half road width in multiples of icon size

        xs_rel = []
        ys_rel = []
        for i in range(N):
            
            b0 = bearings_rad[ i ] % (2*pi)
            b1 = bearings_rad[ (i+1) % N ] % (2*pi)
            
            diff = (b1 - b0 + pi) % (2*pi) - pi
            mean = b0 + .5*diff
            
            r = w / np.sin(diff/2)
            
            xrel_inter = .5+r*np.sin(mean)
            yrel_inter = .5-r*np.cos(mean)
                        
            x0 = xrel_inter + np.sin(b0)
            y0 = yrel_inter - np.cos(b0)

            x2 = xrel_inter + np.sin(b1)
            y2 = yrel_inter - np.cos(b1)
    
            xs_rel += [x0, xrel_inter, x2]
            ys_rel += [y0, yrel_inter, y2]
            
        xs = size * np.array(xs_rel)
        ys = size * np.array(ys_rel)
        
        return xs, ys


    def make_roundabout_outer_polygon(self, bearings_rad, size,ri,w):
        N = len(bearings_rad)
        ri = .1
        w  = .1 # half road width in multiples of icon size

        r = ri + 2*w

        xs_rel = []
        ys_rel = []
        for i in range(N):
            
            b0 = bearings_rad[ i ] % (2*pi)
            b1 = bearings_rad[ (i+1) % N ] % (2*pi)

            phi0 = b0 + np.arcsin(w/r)
            phi1 = b1 - np.arcsin(w/r)

            diff = (phi1 - phi0 + pi) % (2*pi) - pi
            
            n_phi = max( 2, int(diff * 16 / pi) )
            phi = phi0 + np.linspace(0, diff,n_phi, endpoint=True)
            
            x_outer = .5 + r * np.sin(phi)
            y_outer = .5 - r * np.cos(phi)
                                   
            x0 = x_outer[0] + np.sin(b0)
            y0 = y_outer[0] - np.cos(b0)

            x2 = x_outer[-1] + np.sin(b1)
            y2 = y_outer[-1] - np.cos(b1)
    
            xs_rel += [x0] + list(x_outer) + [x2]
            ys_rel += [y0] + list(y_outer) + [y2]
            
        xs = size * np.array(xs_rel)
        ys = size * np.array(ys_rel)
        
        return xs, ys

    def make_arrow(self, size, in_bearing_rad, out_bearing_rad):
        
        delta_b = ( in_bearing_rad - out_bearing_rad + pi ) % (2*pi) - pi
        mean_b = out_bearing_rad + .5 * delta_b

        w = .06
        h = .1
        
        ltail = .5
        lhead = .5-w-h
        
        # Tail
        x0 = .5 + w * np.cos(in_bearing_rad) + ltail * np.sin(in_bearing_rad)
        y0 = .5 + w * np.sin(in_bearing_rad) - ltail * np.cos(in_bearing_rad)
        x2 = .5 - w * np.cos(in_bearing_rad) + ltail * np.sin(in_bearing_rad)
        y2 = .5 - w * np.sin(in_bearing_rad) - ltail * np.cos(in_bearing_rad)
        x1 = .5*(x0+x2) - w * np.sin(in_bearing_rad)
        y1 = .5*(y0+y2) + w * np.cos(in_bearing_rad)

        xt_rel = [x0,x1,x2]
        yt_rel = [y0,y1,y2]
        
        # Flanks
        r = w / np.sin(delta_b/2)
        if delta_b < 0: # left arrow
            # left flank
            xl_rel = [.5-r*np.sin(mean_b)]
            yl_rel = [.5+r*np.cos(mean_b)]
            
            #right flank
            phi = in_bearing_rad + np.linspace(0, -pi-delta_b,10, endpoint=True)
            xr_rel = list( .5 - w * np.cos(phi) )
            yr_rel = list( .5 - w * np.sin(phi) )
            
        else: # right arrow
            
            # right flank
            xr_rel = [.5+r*np.sin(mean_b)]
            yr_rel = [.5-r*np.cos(mean_b)]
            
            #left flank
            phi = out_bearing_rad + np.linspace(0, -pi+delta_b,10, endpoint=True)
            xl_rel = list( .5 - w * np.cos(phi) )
            yl_rel = list( .5 - w * np.sin(phi) )
            
        # Head start
        x0 = .5 + w * np.cos(out_bearing_rad) + lhead * np.sin(out_bearing_rad)
        y0 = .5 + w * np.sin(out_bearing_rad) - lhead * np.cos(out_bearing_rad)
        x4 = .5 - w * np.cos(out_bearing_rad) + lhead * np.sin(out_bearing_rad)
        y4 = .5 - w * np.sin(out_bearing_rad) - lhead * np.cos(out_bearing_rad)
        
        # head - straight out
        x1 = x0 + h * np.cos(out_bearing_rad)
        y1 = y0 + h * np.sin(out_bearing_rad)
        x3 = x4 - h * np.cos(out_bearing_rad) 
        y3 = y4 - h * np.sin(out_bearing_rad)
        
        # head tip
        x2 = .5*(x0+x4) + (w+h) * np.sin(out_bearing_rad)
        y2 = .5*(y0+y4) - (w+h) * np.cos(out_bearing_rad)
        
        xh_rel = [x0,x1,x2,x3,x4]
        yh_rel = [y0,y1,y2,y3,y4]
        
        xs = size * np.array( xt_rel + xr_rel + xh_rel + xl_rel + [xt_rel[0]] )
        ys = size * np.array( yt_rel + yr_rel + yh_rel + yl_rel + [yt_rel[0]] )
   
        return xs, ys


    def make_uturn_arrow(self, size, left_driving=False):
                
        w = .1
        h = .1
        gap = .1
        
        ltail = .45
        lhead = .45-w-h

        rin = 0.5 * (h+gap)
        
        phi = np.linspace(0,pi)
        
        xinarc = list( 0.5 + rin * np.cos(phi) )
        yinarc = list( 0.5 - rin * np.sin(phi) )
        
        xoutarc = list( 0.5 + (rin+2*w) * np.cos(phi[::-1]) )
        youtarc = list( 0.5 - (rin+2*w) * np.sin(phi[::-1]) )
        

        # Head start
        x0 = .5 -rin
        y0 = .5 + lhead 
        x4 = .5 - 2*w - rin
        y4 = .5 + lhead 
        
        # head - straight out
        x1 = x0 + h 
        y1 = y0
        x3 = x4 - h 
        y3 = y4 
        
        # head tip
        x2 = .5*(x0+x4)
        y2 = .5*(y0+y4) + (w+h)
        
        xh_rel = [x0,x1,x2,x3,x4]
        yh_rel = [y0,y1,y2,y3,y4]        
        
        # Tail
        x0 = .5 + rin + 2*w
        y0 = .5 + ltail
        x2 = .5 + rin
        y2 = y0
        x1 = .5 * (x0+x2)
        y1 = y0 - w
        
        xt_rel = [x0,x1,x2]
        yt_rel = [y0,y1,y2]
        
        xs = size * np.array( xinarc + xh_rel + xoutarc + xt_rel + [xinarc[0]])
        ys = size * np.array( yinarc + yh_rel + youtarc + yt_rel + [yinarc[0]])
        
        if left_driving:
            xs = self.size - xs
         
        return xs, ys


    def make_roundabout_arrow(self, size, r, in_bearing_rad, out_bearing_rad):
        """
        @param r: radius of arrow center
        """
        
        w = .06
        h = .1
        
        ltail = .5
        lhead = .5-w-h
        
        # Tail
        x0 = .5 + w * np.cos(in_bearing_rad) + ltail * np.sin(in_bearing_rad)
        y0 = .5 + w * np.sin(in_bearing_rad) - ltail * np.cos(in_bearing_rad)
        x2 = .5 - w * np.cos(in_bearing_rad) + ltail * np.sin(in_bearing_rad)
        y2 = .5 - w * np.sin(in_bearing_rad) - ltail * np.cos(in_bearing_rad)
        x1 = .5*(x0+x2) - w * np.sin(in_bearing_rad)
        y1 = .5*(y0+y2) + w * np.cos(in_bearing_rad)

        xt_rel = [x0,x1,x2]
        yt_rel = [y0,y1,y2]
                          
        # right flank
        phi0r = in_bearing_rad - np.arcsin(w/(r+w))
        phi1r = out_bearing_rad + np.arcsin(w/(r+w))
        delta_phir = (phi0r-phi1r) % (2*pi)
        phir  = np.linspace(phi0r, phi0r-delta_phir, endpoint=True)
        xr_rel = list(.5+(r+w)*np.sin(phir))
        yr_rel = list(.5-(r+w)*np.cos(phir))
        
        #left flank     
        alpha = out_bearing_rad - pi/2 - np.linspace(0,1.3)
        beta  = in_bearing_rad + pi - np.linspace(0,1.3)

        phi0l = out_bearing_rad +.2
        phi1l = in_bearing_rad -.2
        delta_phil = (phi1l-phi0l) % (2*pi)
        phil = np.linspace( phi0l, phi0l + delta_phil)
        
        xarc0 = list( xr_rel[-1] + 2*w * np.sin(alpha) )
        yarc0 = list( yr_rel[-1] - 2*w * np.cos(alpha) )

        xarc1 = list(.5+(r-w)*np.sin(phil))
        yarc1 = list(.5-(r-w)*np.cos(phil))

        xarc2 = list( xr_rel[0] + 2*w * np.sin(beta) )
        yarc2 = list( yr_rel[0] - 2*w * np.cos(beta) )

        xl_rel = xarc0 + xarc1 + xarc2
        yl_rel = yarc0 + yarc1 + yarc2
        
        # Head start
        x0 = .5 + w * np.cos(out_bearing_rad) + lhead * np.sin(out_bearing_rad)
        y0 = .5 + w * np.sin(out_bearing_rad) - lhead * np.cos(out_bearing_rad)
        x4 = .5 - w * np.cos(out_bearing_rad) + lhead * np.sin(out_bearing_rad)
        y4 = .5 - w * np.sin(out_bearing_rad) - lhead * np.cos(out_bearing_rad)
        
        # head - straight out
        x1 = x0 + h * np.cos(out_bearing_rad)
        y1 = y0 + h * np.sin(out_bearing_rad)
        x3 = x4 - h * np.cos(out_bearing_rad) 
        y3 = y4 - h * np.sin(out_bearing_rad)
        
        # head tip
        x2 = .5*(x0+x4) + (w+h) * np.sin(out_bearing_rad)
        y2 = .5*(y0+y4) - (w+h) * np.cos(out_bearing_rad)
        
        xh_rel = [x0,x1,x2,x3,x4]
        yh_rel = [y0,y1,y2,y3,y4]
        
        xs = size * np.array( xt_rel + xr_rel + xh_rel + xl_rel + [xt_rel[0]] )
        ys = size * np.array( yt_rel + yr_rel + yh_rel + yl_rel + [yt_rel[0]] )
               
        return xs, ys

    def make_british_roundabout_arrow(self, size, r, in_bearing_rad, out_bearing_rad):
        xs,ys = self.make_roundabout_arrow(size=size, r=r, in_bearing_rad=(-in_bearing_rad%(2*pi)), out_bearing_rad=(-out_bearing_rad%(2*pi)))
        return self.size-xs, ys
    
    def make_triangle( self, size, a_rel, rel_radius=.1):
        
        hmax = 0.5 * np.sqrt(3)
        h = a_rel * hmax
        left  = 0.5 - .5*a_rel
        right = 0.5 + .5*a_rel
        bot   = 0.5 + (.5*np.sqrt(3)-.5)*h - (.5*np.sqrt(3)-.5)*hmax +.5*hmax
        top   = bot - h
        
        phi = np.linspace(0, 2/3.*pi, endpoint=True)
        
        x_redge = right - rel_radius + rel_radius * np.sin(phi)
        y_redge = bot  - rel_radius + rel_radius * np.cos(phi)

        x_ledge = left + rel_radius + rel_radius * np.sin(phi+4/3*pi)
        y_ledge = bot  - rel_radius + rel_radius * np.cos(phi+4/3*pi)

        x_tedge = 0.5              + rel_radius * np.sin(phi-4/3*pi)
        y_tedge = top + rel_radius + rel_radius * np.cos(phi-4/3*pi)
        
        xs = np.hstack([x_ledge, x_redge, x_tedge, [x_ledge[0]]]) * size
        ys = np.hstack([y_ledge, y_redge, y_tedge, [y_ledge[0]]]) * size
        return xs, ys

class Crossing(DirectionIcon):
    def __init__(self, in_bearing_deg=0, out_bearing_deg=0, bearings_deg=[], size=32, left_driving=False):
        DrawingAreaButton.__init__(self, size=size)
    
        self.bearings_rad = np.array(bearings_deg) * pi / 180.0
        self.size = size
        
        self.x_street, self.y_street = self.make_street_polygon( bearings_rad = self.bearings_rad, size = self.size )
        self.x_arrow,  self.y_arrow  = self.make_arrow(size=self.size, in_bearing_rad = in_bearing_deg * pi/180, out_bearing_rad = out_bearing_deg *pi/180)
        
    def on_draw(self, da, ctx):
        
        ctx.set_source_rgb(.6,1,.6)
        ctx.rectangle(0,0,self.size,self.size)
        ctx.fill()

        self.polygon( ctx, self.x_street, self.y_street )
        ctx.set_source_rgb(0,0,0)
        ctx.stroke_preserve()
        ctx.set_source_rgb(1,1,1)
        ctx.fill()
              
        self.polygon( ctx, self.x_arrow, self.y_arrow )
        ctx.set_source_rgb(0,0,.3)
        ctx.fill_preserve()
        ctx.set_source_rgb(0,0,0)
        ctx.stroke()


class Roundabout(Crossing):
    def __init__(self, in_bearing_deg=0, out_bearing_deg=0, bearings_deg=[], size=32, left_driving=False):
        DrawingAreaButton.__init__(self, size=size)
    
        ri = .1
        w  = .1
    
        self.bearings_rad = np.array(bearings_deg) * pi / 180.0
        self.size = size
        
        self.x_outer, self.y_outer = self.make_roundabout_outer_polygon( bearings_rad = self.bearings_rad, size = self.size, ri=ri, w=w )
        if left_driving:
            self.x_arrow,  self.y_arrow  = self.make_british_roundabout_arrow(size=self.size, r = ri+w, in_bearing_rad = in_bearing_deg * pi/180, out_bearing_rad = out_bearing_deg *pi/180)
        else:
            self.x_arrow,  self.y_arrow  = self.make_roundabout_arrow(size=self.size, r = ri+w, in_bearing_rad = in_bearing_deg * pi/180, out_bearing_rad = out_bearing_deg *pi/180)
            
        self.ri_abs  = ri * self.size
        self.ri_xpos = .5 * self.size
        self.ri_ypos = .5 * self.size


    def on_draw(self, da, ctx):
        
        ctx.set_source_rgb(.6,1,.6)
        ctx.rectangle(0,0,self.size,self.size)
        ctx.fill()

        self.polygon( ctx, self.x_outer, self.y_outer )
        ctx.set_source_rgb(0,0,0)
        ctx.stroke_preserve()
        ctx.set_source_rgb(1,1,1)
        ctx.fill()

        ctx.arc(self.ri_xpos, self.ri_ypos, self.ri_abs, 0, 2*pi)
        ctx.set_source_rgb(0,0,0)
        ctx.stroke_preserve()
        ctx.set_source_rgb(.6,1,.6)
        ctx.fill()

        self.polygon( ctx, self.x_arrow, self.y_arrow )
        ctx.set_source_rgb(0,0,.3)
        ctx.fill_preserve()
        ctx.set_source_rgb(0,0,0)
        ctx.stroke()
        
        
class CheckerFlag(DirectionIcon):
    def __init__(self, in_bearing_deg=0, out_bearing_deg=0, bearings_deg=[], size=32, left_driving=False):
        DrawingAreaButton.__init__(self, size=size)
    
        self.size = size
        self.checksize = size / 5
                
    def on_draw(self, da, ctx):
        
        ctx.set_source_rgb(1,1,1)
        ctx.rectangle(0,0,self.size,self.size)
        ctx.fill()
        
        ctx.set_source_rgb(0,0,0)
        for x0 in 2 * self.checksize * np.arange(3):
            for y0 in 2 * self.checksize * np.arange(3):
                ctx.rectangle(x0, y0,self.checksize,self.checksize)
                ctx.fill()

        for x0 in self.checksize * (1+2*np.arange(2)):
            for y0 in self.checksize * (1+2*np.arange(2)):
                ctx.rectangle(x0, y0,self.checksize,self.checksize)
                ctx.fill()


class UTurn(DirectionIcon):
    def __init__(self, in_bearing_deg=0, out_bearing_deg=0, bearings_deg=[], size=32, left_driving=False):
        DrawingAreaButton.__init__(self, size=size)
    
        self.size = size
        
        self.x_arrow,  self.y_arrow  = self.make_uturn_arrow(size=self.size, left_driving = left_driving )
        
    def on_draw(self, da, ctx):
        
        ctx.set_source_rgb(1,1,1)
        ctx.rectangle(0,0,self.size,self.size)
        ctx.fill()
              
        self.polygon( ctx, self.x_arrow, self.y_arrow )
        ctx.set_source_rgb(.8,0,0)
        ctx.fill_preserve()
        ctx.set_source_rgb(0,0,0)
        ctx.stroke()
        
class NESWArrow(DirectionIcon):
    def __init__(self, in_bearing_deg=0, out_bearing_deg=0, bearings_deg=[], size=32, left_driving=False):
        DrawingAreaButton.__init__(self, size=size)
        bearing_rad = out_bearing_deg * pi/180.
        self.size = size
        self.x_arrow,  self.y_arrow  = self.make_arrow(size=self.size, in_bearing_rad = bearing_rad+pi, out_bearing_rad = bearing_rad)

        self.fontsize = int(round(.2 * size))
        self.halfsize = 0.5 * size
        self.roseradius = 0.5 * size - 1

    def on_draw(self, da, ctx):
        
        ctx.set_font_size (30)
        text_extents = ctx.text_extents( "N" )
        n_width = text_extents.width
        n_height = text_extents.height
        
        ctx.set_source_rgb(1,1,1)
        ctx.rectangle(0,0,self.size,self.size)
        ctx.fill()
        
        ctx.set_source_rgb(0,0,0)
        ctx.arc(self.halfsize, self.halfsize, self.roseradius, 0, 2*pi)
        ctx.stroke()
        
        ctx.move_to( self.halfsize - .5* n_width, n_height + 5 )
        ctx.show_text("N")
        ctx.move_to( self.size-n_width-5, self.halfsize + .5*n_height )
        ctx.show_text("E")
        ctx.move_to( self.halfsize - .5* n_width, self.size - 5 )
        ctx.show_text("S")
        ctx.move_to( 5, self.halfsize + .5*n_height )
        ctx.show_text("W")
        
        
        ctx.set_source_rgba(0,0,0.3,.8)
        self.polygon( ctx, self.x_arrow, self.y_arrow )
        ctx.fill()


class Notification(DirectionIcon):
    def __init__(self, in_bearing_deg=0, out_bearing_deg=0, bearings_deg=[], size=32, left_driving=False):
        DrawingAreaButton.__init__(self, size=size)
        self.size = size
        
        self.x_outer, self.y_outer = self.make_triangle( size = size, a_rel = 1, rel_radius=.03)
        self.x_inner, self.y_inner = self.make_triangle( size = size, a_rel = .7, rel_radius=0)
    
        self.xdot = .5 * size
        self.ydot = .765 * size
        self.dot_radius = .045*size
        
        self.y_upper = .395*size
        self.y_lower = .67*size
        self.upper_radius = .045*size
        self.lower_radius = .025*size
    
    def on_draw(self, da, ctx):
        ctx.set_source_rgb(1,1,1)
        ctx.rectangle(0,0,self.size,self.size)
        ctx.fill()

        ctx.set_source_rgb(1,0,0)
        self.polygon( ctx, self.x_outer, self.y_outer )
        ctx.fill()

        ctx.set_source_rgb(1,1,1)
        self.polygon( ctx, self.x_inner, self.y_inner )
        ctx.fill()

        ctx.set_source_rgb(0,0,0)
        ctx.arc(self.xdot, self.ydot, self.dot_radius, 0, 2*pi)
        ctx.fill()

        ctx.arc(self.xdot, self.y_upper, self.upper_radius, pi, 0)
        ctx.arc(self.xdot, self.y_lower, self.lower_radius, 0,pi)
        ctx.fill()
