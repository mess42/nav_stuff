#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

import widgets.markers as markers

class MarkerLayerWidget(Gtk.DrawingArea):
    def __init__(self, map_copyright):       
        Gtk.DrawingArea.__init__(self)
        self.connect("draw", self.on_draw)
                
        self.list_of_markers = self.make_marker_list(map_copyright=map_copyright)
        
    def make_marker_list(self, destination = None, map_copyright=""):
        m = []
        
        # Map copyright
        if map_copyright != "":
            m += [markers.FixedXYMarker(draftsman = markers.Text(map_copyright), 
                           xy_rel_to_window_size = [0,1], 
                           xy_abs_offset = [130,-11])]
        
        # Scale bar    
        m += [markers.MetricScaleBarMarker(draftsman = markers.ScaleBar(), 
                           desired_size_px = 50,
                           xy_rel_to_window_size = [0,1], 
                           xy_abs_offset = [20,-25])]
 
        # Destination
        if destination is not None:
            m += [markers.FixedLatLonMarkerWithAlternativeOffTilePointer(
                                        draftsman = markers.Pin(fill_color=(0.8,0,0)),
                                        off_tile_draftsman= markers.ArrowWithOffsetLabel( fill_color=(0.8,0,0)), 
                                        lat_deg = float(destination["lat"]),
                                        lon_deg = float(destination["lon"]),
                                        )]
            
        # Ego marker
        m += [markers.FollowingMarker(draftsman = markers.Pin(fill_color=(0,1,0)))]
        
        self.list_of_markers = m
        return m
    
    def on_draw(self, da, ctx):
        """
        @brief: draw markers overlaid on the map.
        
        @param da (Gtk drawing area object)
        @param ctx (cairo context)
        """        
        for mark in self.list_of_markers:           
            mark.draw(ctx)
            
    def update(self, cropped_tile, position):
        """
        @brief: update the pixel positions of all markers
        """
        for mark in self.list_of_markers:           
            mark.update(cropped_tile, position)
        
    
        