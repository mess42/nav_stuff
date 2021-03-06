#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import numpy as np
import helpers.round

class Marker(object):
    def __init__(self, draftsman, **params):
        self.draftsman = draftsman
        self.x       = 0
        self.y       = 0
        self.heading = 0
        self.dx_px = 0   # can the marker not be drawn where originally intended ?
        self.dy_px = 0
        self.dx_m  = 0
        self.dy_m  = 0
        
    def draw(self, ctx):
        self.draftsman.draw( ctx, 
                             x           = self.x, 
                             y           = self.y, 
                             heading_rad = self.heading,
                             dx_px       = self.dx_px,
                             dy_px       = self.dy_px,
                             dx_m        = self.dx_m,
                             dy_m        = self.dy_m
                           )
    
    def update(self, cropped_tile, position):
        raise NotImplementedError("This is a base class")


class FixedXYMarker(Marker):
    def __init__(self, draftsman, xy_rel_to_window_size = [0,0], xy_abs_offset = [0,0] ):
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
        Marker.__init__(self, draftsman)
        self.xy_rel_to_window_size = xy_rel_to_window_size 
        self.xy_abs_offset         = xy_abs_offset
    
    def update(self, cropped_tile, position):
        self.x = self.xy_rel_to_window_size[0] * cropped_tile.xsize_px + self.xy_abs_offset[0]
        self.y = self.xy_rel_to_window_size[1] * cropped_tile.ysize_px + self.xy_abs_offset[1]

    
class FixedLatLonMarker(Marker):
    def __init__(self, draftsman, lat_deg, lon_deg):
        """
        @brief: Marker with a fixed position in latitude and longitude.
        
        @param draftsman (draftsman object)
        @param lat_deg (float or 1d numpy array)
        @param lon_deg (float or 1d numpy array)
            type (float or array) must be chosen 
            to fit the draftsman.draw() arguments.
        
        Use for fixed objects like 
        destination, waypoints, points of interest, polygon lines.
        """
        Marker.__init__(self, draftsman)
        self.lat_deg = lat_deg
        self.lon_deg = lon_deg

    def update(self,cropped_tile, position):
        self.y, self.x = cropped_tile.angles_to_pxpos(lat_deg = self.lat_deg, lon_deg = self.lon_deg)


class FixedLatLonMarkerWithAlternativeOffTilePointer(Marker):
    def __init__(self, draftsman, off_tile_draftsman, lat_deg, lon_deg):
        """
        @brief: Marker with a fixed position in latitude and longitude.
        If the position is off the tile, and alternative marker is placed
        at the border of the tile, pointing towards the position.
        
        Use for fixed objects like Destination, waypoints, or points of interest.
        """
        Marker.__init__(self, draftsman)
        self.on_tile_draftsman  = self.draftsman
        self.off_tile_draftsman = off_tile_draftsman
        self.lat_deg = lat_deg
        self.lon_deg = lon_deg
        self.border = 10 # how close to the boder is "off tile" ?


    def update(self,cropped_tile, position):
        y,x = cropped_tile.angles_to_pxpos(lat_deg = self.lat_deg, lon_deg = self.lon_deg)
        
        self.x = x
        self.y = y
        
        # Heading is from the screen center to the pin position
        # This should stay like that: If this was the distance to the ego position, and both marker and ego position are off-tile, this would result in a strange looking arrow
        self.heading = np.arctan2( self.x - cropped_tile.xsize_px//2, cropped_tile.ysize_px//2 - self.y )

        self.draftsman = self.on_tile_draftsman
        
        if (self.x < self.border):
            self.draftsman = self.off_tile_draftsman
            self.x      = self.border
            self.y      = cropped_tile.ysize_px//2 - ( self.x - cropped_tile.xsize_px//2 ) / np.tan(self.heading)
        elif (self.x > cropped_tile.xsize_px - self.border):
            self.draftsman = self.off_tile_draftsman
            self.x      = cropped_tile.xsize_px - self.border
            self.y      = cropped_tile.ysize_px//2 - ( self.x - cropped_tile.xsize_px//2 ) / np.tan(self.heading)

        if (self.y < self.border):
            self.draftsman = self.off_tile_draftsman
            self.y      = self.border
            self.x      = cropped_tile.xsize_px//2 + (cropped_tile.ysize_px//2 - self.y ) * np.tan(self.heading)
        elif (self.y > cropped_tile.ysize_px - self.border):
            self.draftsman = self.off_tile_draftsman
            self.y      = cropped_tile.ysize_px - self.border
            self.x      = cropped_tile.xsize_px//2 + (cropped_tile.ysize_px//2 - self.y ) * np.tan(self.heading)

        self.dx_px = x-self.x
        self.dy_px = y-self.y
        self.dx_m  = self.dx_px * cropped_tile.scale_in_m_per_px
        self.dy_m  = self.dy_px * cropped_tile.scale_in_m_per_px
            
            
            
            
                  
class FollowingMarker(Marker):
    """
    @brief: Marker that follows the ego position.
    """
    def update( self, cropped_tile, position):
        self.y, self.x = cropped_tile.angles_to_pxpos(lat_deg = position.latitude, lon_deg = position.longitude )
        self.heading = position.heading


class MetricScaleBarMarker(FixedXYMarker):
    def __init__(self, draftsman, xy_rel_to_window_size = [0,0], xy_abs_offset = [0,0], desired_size_px=50):
        if type(draftsman) != ScaleBar:
            raise Exception("This marker type requires an instance of ScaleBar as draftsman.")
        FixedXYMarker.__init__(self, draftsman=draftsman, xy_rel_to_window_size = xy_rel_to_window_size, xy_abs_offset=xy_abs_offset)
        self.desired_size_px   = desired_size_px
        
        # all candidate sizes from 1 km on must be integer multiples of 1 km for the following label code to work.
        self.candidate_sizes_m = np.array([10,20,50,100,200,500,1000,2000,5000,10000,20000,50000,100000,200000,500000,1000000])
        
        self.candidate_labels = []
        for i in range(len(self.candidate_sizes_m)):
            if self.candidate_sizes_m[i] < 1000:
                s = str(self.candidate_sizes_m[i]) + " m"
            else:
                s = str(self.candidate_sizes_m[i]//1000) + " km" 
            self.candidate_labels.append(s)

    def update(self, cropped_tile, position):
        candidate_sizes_px = self.candidate_sizes_m / cropped_tile.scale_in_m_per_px
        
        # Find the scale size closest to the desired one
        i = np.argmin(abs(candidate_sizes_px - self.desired_size_px))
        
        self.draftsman.xsize = int(round(candidate_sizes_px[i]))
        self.draftsman.ysize = 15
        self.draftsman.label = self.candidate_labels[i]
        
        self.x = self.xy_rel_to_window_size[0] * cropped_tile.xsize_px + self.xy_abs_offset[0]
        self.y = self.xy_rel_to_window_size[1] * cropped_tile.ysize_px + self.xy_abs_offset[1]


class Draftsman(object):
    def __init__(self, **params):
        """
        @brief: stores geometry and layout parameters to later draw a marker.
        """
        raise NotImplementedError()
        
    def draw(self, ctx, x, y, heading_rad, dx_px=0, dy_px=0, dx_m=0, dy_m=0):
        """
        @brief: draw the marker.
        
        @param ctx (Cairo context)
        @param x (int) reference position of the marker in px
        @param y (int) reference position of the marker in px
               The ref position depends on the Draftsman type and configuration.
               It can be, for example, the tip apex of an arrow
        @param heading_rad (float) Rotation of the marker. 
               0 is north, pi/2 is east, pi is south, 3/2 pi is west.
        @param dx_px (int) Marker shift in px
        @param dy_px (int) Marker shift in px
        @param dx_m (float) Marker shift in m
        @param dy_m (float) Marker shift in m
               If the marker can, for some reason, not be drawn where
               it was originally desired to draw it, this can be indicated
               by dx,dy. For example, if the originally intended x,y were outside
               the window size, but the marker shall be drawn inside the window.
               
               The marker __will__ be drawn at params x,y.
               
               dx and dy indicate the difference between x,y and
               the originally desired position.
               Some Draftsman classes can draw themselves differently
               to indicate the offset, for example by writing the distance
               next to the marker.
        """
        raise NotImplementedError()

class Dot(Draftsman):
    def __init__(self, 
                 radius=10, 
                 fill_color=(1,0,0), 
                 border_color=(0,0,0),
                 ):
        self.radius       = radius
        self.fill_color   = fill_color
        self.border_color = border_color
        
    def draw(self, ctx, x, y, heading_rad, dx_px=0, dy_px=0, dx_m=0, dy_m=0):
        
        ctx.move_to(x,y)
        ctx.arc( x , y, self.radius, 0, 2*np.pi)
        
        # fill and stroke the dot
        ctx.set_source_rgb(*self.border_color)
        ctx.stroke_preserve()
        ctx.set_source_rgb(*self.fill_color)
        ctx.fill()


class Pin(Draftsman):
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
        
    def draw(self, ctx, x, y, heading_rad, dx_px=0, dy_px=0, dx_m=0, dy_m=0):
        
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


class ScaleBar(Draftsman):
    def __init__(self, size_px=50, label="1 arbitrary unit", color=(0,0,0)):
        self.color =color
        self.xsize = size_px
        self.ysize = 0.2 * size_px
        self.label = label
        
    def draw(self, ctx, x, y, heading_rad, dx_px=0, dy_px=0, dx_m=0, dy_m=0):
        ctx.set_source_rgb(*self.color)
        ctx.rectangle(x,y, self.xsize, self.ysize)
        ctx.fill()
        ctx.move_to( x+self.xsize+5, y+self.ysize-1 )
        ctx.show_text( self.label )


class Arrow(Draftsman):
    def __init__(self, width=20, 
                 length = 40,
                 center = 0,
                 fill_color=(1,0,0), 
                 border_color=(0,0,0),
                 ):
        """
        @param width (float) arrow head width 
        @param length (float) total length
        @param center (float) center position relative to arrow length
                              0 means the draw methods draws the head on (x,y)
                              1 means the draw methods draws the tail on (x,y)
                              This is also the center of rotation
        @param fill_color (list of 3 float)
        @param border_color (list of 3 float)
        """
        self.fill_color = fill_color
        self.border_color = border_color
        
        # define half the arrow
        self.dx = width  *             np.array([0, 0.5, 0.15, 0.3, 0  ])
        self.dy = length * (- center + np.array([0, 0.5, 0.4 , 1  , 0.9]))
        
        # autocomplete symmetrically
        self.dx = np.hstack([self.dx, -self.dx[:-1][::-1] ])
        self.dy = np.hstack([self.dy,  self.dy[:-1][::-1] ])
        
    def draw(self, ctx, x, y, heading_rad, dx_px=0, dy_px=0, dx_m=0, dy_m=0):        
        xs = x + np.cos(heading_rad) * self.dx - np.sin(heading_rad) * self.dy
        ys = y + np.sin(heading_rad) * self.dx + np.cos(heading_rad) * self.dy
        
        # draw polygon
        ctx.move_to(xs[0],ys[0])
        for i in np.arange(len(xs)-1)+1:
            ctx.line_to(xs[i], ys[i])
        
        # fill and stroke the outline
        ctx.set_source_rgb(*self.border_color)
        ctx.stroke_preserve()
        ctx.set_source_rgb(*self.fill_color)
        ctx.fill()
        

class Text(Draftsman):
    def __init__(self, label, fontsize=10, color=(0,0,0)):
        self.color = color
        self.label  = label
        self.width = 0
        self.height = 0
        self.fontsize = fontsize
        
    def draw(self, ctx, x, y, heading_rad, dx_px=0, dy_px=0, dx_m=0, dy_m=0):
        ctx.set_font_size (self.fontsize)
        text_extents = ctx.text_extents( self.label )
        self.width = text_extents.width
        self.height = text_extents.height
        
        ctx.set_source_rgb(*self.color)
        ctx.move_to( x, y )
        ctx.show_text( self.label )


class ArrowWithOffsetLabel(Draftsman):
    def __init__(self, width=20, 
                 length = 40,
                 center = 0,
                 fill_color=(1,0,0), 
                 border_color=(0,0,0),
                 ):
        self.arrow          = Arrow( width=width, length = length, center = center, fill_color=fill_color, border_color=border_color )
        self.text           = Text( label = "", fontsize = .5*length, color=fill_color)
        self.arrow_length   = max(  np.sqrt( self.arrow.dx**2 + self.arrow.dy**2 )  )
          
    def draw(self, ctx, x, y, heading_rad, dx_px=0, dy_px=0, dx_m=0, dy_m=0):

        self.arrow.draw(ctx, x, y, heading_rad)
                        
        if dx_m != 0 or dy_m != 0:

            beta = 30
            heading_deg_plus_beta = (heading_rad * 180/np.pi + beta) % 360

            offset_m = np.sqrt(dx_m**2+dy_m**2)

            # TODO: find a shorter more elegant code with less if-statements
            if   heading_deg_plus_beta > 0            and heading_deg_plus_beta <= 2*beta:
                #north
                dx = -self.text.width * heading_deg_plus_beta / (2*beta)
                dy =  self.text.height
            elif heading_deg_plus_beta > 2*beta       and heading_deg_plus_beta <= 90:
                # north_east
                dx = -self.text.width
                dy =  self.text.height
            elif heading_deg_plus_beta > 90           and heading_deg_plus_beta <= 90 + 2*beta:
                # east
                dx = -self.text.width
                dy =  self.text.height * (1-(heading_deg_plus_beta - 90)/(2*beta))
            elif heading_deg_plus_beta > 90 + 2*beta  and heading_deg_plus_beta <= 180:
                # south east
                dx = -self.text.width
                dy =  0
            elif heading_deg_plus_beta > 180          and heading_deg_plus_beta <= 180 + 2*beta:
                # south
                dx =  self.text.width * ((heading_deg_plus_beta - 180)/(2*beta)-1)
                dy =  0
            elif heading_deg_plus_beta > 180 + 2*beta and heading_deg_plus_beta <= 270:
                # south west
                dx =  0
                dy =  0
            elif heading_deg_plus_beta > 270          and heading_deg_plus_beta <= 270 + 2*beta:
                # west
                dx =  0
                dy = self.text.height * (heading_deg_plus_beta-270)/(2*beta)
            else:
                # north_west
                dx = 0
                dy = self.text.height
           
            xtext = x + dx - np.sin(heading_rad) * (self.arrow_length + 5)
            ytext = y + dy + np.cos(heading_rad) * (self.arrow_length + 5)

            blocks = helpers.round.distance_to_rounded_textblocks( distance_in_m = offset_m )
            self.text.label = blocks["distance"] + " " + blocks["distance_unit_abbrev"]
            self.text.draw(ctx, xtext, ytext, heading_rad)
            

class PolygonLine(Draftsman):
    def __init__(self, 
                 color_rgba = (0,0,0,1),
                 linewidth_px = 10
                 ):
        self.color_rgba = color_rgba
        self.linewidth_px = linewidth_px
                
    def draw(self, ctx, x, y, heading_rad, dx_px=0, dy_px=0, dx_m=0, dy_m=0):
                
        ctx.set_line_width(self.linewidth_px)
        ctx.set_source_rgba(*self.color_rgba)
        
        ctx.move_to(x[0], y[0])        
        for i in np.arange(len(x)-1)+1:
            ctx.line_to(x[i] , y[i])

        ctx.stroke()
        ctx.set_line_width(1)
