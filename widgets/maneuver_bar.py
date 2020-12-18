#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gdk, GLib

import numpy as np
import widgets.maneuver_icons


class ManeuverBar(Gtk.Box):
    def __init__(self, orientation = Gtk.Orientation.HORIZONTAL ):
        Gtk.Window.__init__(self, orientation=orientation, spacing=10)
        
        self.maneuvers = []

    def get_icon_class_by_name(self,name):
        d = { "arrive"       : widgets.maneuver_icons.CheckerFlag,
              "crossing"     : widgets.maneuver_icons.Crossing,
              "nesw_arrow"   : widgets.maneuver_icons.NESWArrow,
              "notification" : widgets.maneuver_icons.Notification,
            }
        return d[name]

    
    def set_new_route(self, maneuvers_with_direction_data):
        self.maneuvers = maneuvers_with_direction_data
        
        for child in self.get_children():
            self.remove(child)
            
        for i_man in np.arange(3):
            icon = self.new_maneuver_widget(maneuver=self.maneuvers[i_man], size_px=120) 
            self.add( icon )
        self.set_size_request(360,120) # TODO: hard coded size !!!!
        self.show_all()
   

    def new_maneuver_widget(self, maneuver, size_px):
        text_blocks = maneuver["text_blocks"]
 
        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        
        # TODO: round distance using calc.round
        top_txt = text_blocks["distance_preposition"]  + " " + str(maneuver["distance_before"]) + " m"
        top_label = Gtk.Label( top_txt )

        IconClass = self.get_icon_class_by_name( maneuver["icon_type"] )
        icon = IconClass(in_bearing_deg  = maneuver["in_bearing_deg"], 
                                            out_bearing_deg = maneuver["out_bearing_deg"], 
                                            bearings_deg    = maneuver["bearings_deg"], 
                                            size            = size_px, 
                                            left_driving    = maneuver["left_driving"],
                                            )
        bot_txt = text_blocks["to_preposition"] + " " + text_blocks["street_name_after"]
        bot_label = Gtk.Label(bot_txt)
        bot_label.set_line_wrap(True) 
        
        vbox.add(top_label)
        vbox.add(icon)
        vbox.add(bot_label)
        return vbox