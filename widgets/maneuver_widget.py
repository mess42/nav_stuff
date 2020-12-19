#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

import numpy as np

import helpers.round

import widgets.maneuver_icons


class ManeuverWidget(Gtk.Box):
    def __init__(self, maneuver, maneuver_id, in_bearing_is_down, size_px):
        Gtk.Box.__init__( self, orientation = Gtk.Orientation.VERTICAL, spacing = 0 )
        
        self.maneuver_id = maneuver_id
        
        text_blocks = maneuver["text_blocks"]
        dist_text_blocks = helpers.round.distance_to_rounded_textblocks(distance_in_m = maneuver["distance_to_prev"] )
        
        top_txt = "+" + dist_text_blocks["distance"] + " " + dist_text_blocks["distance_unit_abbrev"]
        self.top_label = Gtk.Label( top_txt )

        IconClass        = self.get_icon_class_by_name( maneuver["icon_type"] )
        delta = 0
        if in_bearing_is_down and not np.isnan(maneuver["in_bearing_deg"]):
            delta = 180 - maneuver["in_bearing_deg"]
        icon_in_bearing  = maneuver["in_bearing_deg"] + delta
        icon_out_bearing = maneuver["out_bearing_deg"] + delta
        icon_bearings    = maneuver["bearings_deg"] + delta
        self.icon = IconClass(in_bearing_deg  = icon_in_bearing, 
                              out_bearing_deg = icon_out_bearing, 
                              bearings_deg    = icon_bearings, 
                              size            = size_px, 
                              left_driving    = maneuver["left_driving"],
                              )
        bot_txt = text_blocks["to_preposition"] + " " + text_blocks["street_name_after"]
        self.bot_label = Gtk.Label(bot_txt)
        self.bot_label.set_line_wrap(True) 
        
        self.add(self.top_label)
        self.add(self.icon)
        self.add(self.bot_label)


    def get_icon_class_by_name(self,name):
        d = { "arrive"       : widgets.maneuver_icons.CheckerFlag,
              "crossing"     : widgets.maneuver_icons.Crossing,
              "nesw_arrow"   : widgets.maneuver_icons.NESWArrow,
              "notification" : widgets.maneuver_icons.Notification,
            }
        return d[name]
    
    
    def set_top_text(self, text):
        self.top_label.set_text( text )