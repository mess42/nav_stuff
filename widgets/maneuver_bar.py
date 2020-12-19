#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gdk, GLib

import numpy as np

import widgets.maneuver_widget
import helpers.angles


class ManeuverBar(Gtk.Box):
    def __init__(self, in_bearing_is_down = True, orientation = Gtk.Orientation.HORIZONTAL ):
        Gtk.Window.__init__(self, orientation=orientation, spacing=10)
        
        self.maneuvers = []
        self.maneuver_widgets = []
        self.in_bearing_is_down = in_bearing_is_down

    
    def set_new_route(self, maneuvers_with_direction_data):
        self.maneuvers = maneuvers_with_direction_data
        self.remake_all_widgets()

    def remake_all_widgets(self):
        """
        @param in_bearing_is_down (bool)
            If True, the icon is tilted so that the arrow comes from the bottom.
            If False, the icon top is north.
        """
        self.maneuver_widgets = []
        for child in self.get_children():
            self.remove(child)
            
        for i_man in np.arange(5):
            man_widget = widgets.maneuver_widget.ManeuverWidget(
                             maneuver = self.maneuvers[i_man], 
                             maneuver_id = i_man, 
                             in_bearing_is_down = self.in_bearing_is_down, 
                             size_px = 120) 
            self.maneuver_widgets.append( man_widget )
            self.add( man_widget )
        self.set_size_request(360,120) # TODO: hard coded size !!!!
        self.show_all()
   
    
    def update(self, lat_deg, lon_deg, in_bearing_is_down ):
        
        if in_bearing_is_down != self.in_bearing_is_down:
            self.in_bearing_is_down = in_bearing_is_down
            self.remake_all_widgets()
        
        if len(self.maneuver_widgets) != 0:
            i = self.maneuver_widgets[0].maneuver_id

            loc = self.maneuvers[i]["location"]
            dist = helpers.angles.haversine_distance(lat1_deg=loc[1], lon1_deg=loc[0], lat2_deg=lat_deg, lon2_deg=lon_deg)

            self.maneuver_widgets[0].set_top_text(str(round(dist)))
    