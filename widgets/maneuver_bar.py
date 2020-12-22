#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gdk, GLib

import numpy as np

import widgets.maneuver_widget
import helpers.angles


class ManeuverBar(Gtk.Box):
    def __init__(self, number_of_widgets = 3, in_bearing_is_down = True, pos_tolerance = 20, orientation = Gtk.Orientation.HORIZONTAL ):
    
        Gtk.Window.__init__(self, orientation=orientation, spacing = 10)
        
        self.maneuvers = []
        self.in_bearing_is_down = in_bearing_is_down
        self.search_index_range = [0,0]
        self.pos_tolerance = pos_tolerance
        self.number_of_widgets = number_of_widgets
        
    
    def set_new_route(self, maneuvers_with_direction_data):
        self.maneuvers = maneuvers_with_direction_data
        
        if len(self.maneuvers) != 0:
            self.search_index_range = self.get_search_range( i_maneuver = 0)
        else:
            self.search_index_range = [0,0]

        self.remake_all_widgets(i_start=0, number_of_widgets=self.number_of_widgets)


    def get_search_range(self, i_maneuver, overlap_distance = 200 ):
        dist_from_start = self.maneuvers[i_maneuver]["distances_from_route_start"]
        no_points = len(dist_from_start)

        man_i_on_route = self.maneuvers[i_maneuver]["ind_on_route"]
        man_dist_from_start = dist_from_start[man_i_on_route]
        
        indices_with_short_distance = (i for i in np.arange(no_points) if dist_from_start[i] <= man_dist_from_start - overlap_distance )
        imin = next(  indices_with_short_distance, 0 )
        
        # TODO: do not start from 0, but from man_i_on_route
        indices_with_large_distance = (i for i in np.arange(no_points) if dist_from_start[i] >= man_dist_from_start + overlap_distance )
        imax = max( 0, next(  indices_with_large_distance,  len(self.maneuvers[0]["route_lat_deg"])-1 ) )
        
        return [imin, imax]

    def remake_all_widgets(self, i_start, number_of_widgets):
        for child in self.get_children():
            self.remove(child)
        self.set_size_request(0,0)

        number_of_widgets = min(number_of_widgets, len(self.maneuvers) )
        for i_man in np.arange( number_of_widgets ) + i_start:
            self.add_a_widget(i_man)


    def add_a_widget(self, i_man):
        man_widget = widgets.maneuver_widget.ManeuverWidget(
                         maneuver = self.maneuvers[i_man], 
                         maneuver_id = i_man, 
                         in_bearing_is_down = self.in_bearing_is_down, 
                         size_px = 120) # TODO: hard coded size !!!!
        self.add( man_widget )
        self.set_size_request(360,120) # TODO: hard coded size !!!!
        self.show_all()
        
    
    def update(self, lat_deg, lon_deg, in_bearing_is_down ):
        
        # check if auto-rotate was toggled
        if in_bearing_is_down != self.in_bearing_is_down:
            self.in_bearing_is_down = in_bearing_is_down
            self.remake_all_widgets( i_start = self.get_children()[0].maneuver_id, number_of_widgets = self.number_of_widgets)
        
        # check if the current position is in the search range
        if len(self.get_children()) != 0:
            
            # TODO: make this whole section elegant, 
            # encapsulate
            # less if statements
            # and don't calculate everything on the fly over and over again
            
            man_id = self.get_children()[0].maneuver_id
            
            # slice out a small part of the route
            search_i = self.search_index_range
            route_dists_from_start = self.maneuvers[man_id]["distances_from_route_start"][ search_i[0] : search_i[1] ]
            route_lats_deg         = self.maneuvers[man_id]["route_lat_deg"][ search_i[0] : search_i[1] ]
            route_lons_deg         = self.maneuvers[man_id]["route_lon_deg"][ search_i[0] : search_i[1] ]
            route_i_man            = self.maneuvers[man_id]["ind_on_route"] - search_i[0]
                       
            a_rel, mindist = helpers.angles.relation_of_angular_polyline_segments_to_reference_position(
                                 lat_poly_deg = route_lats_deg, 
                                 lon_poly_deg = route_lons_deg, 
                                 lat_ref_deg  = lat_deg, 
                                 lon_ref_deg  = lon_deg)
            
            i_closest_segment = np.argmin(mindist)
            dist_from_start = route_dists_from_start[i_closest_segment] + a_rel[i_closest_segment] * (route_dists_from_start[i_closest_segment+1]-route_dists_from_start[i_closest_segment])           

            if dist_from_start - route_dists_from_start[route_i_man] > self.pos_tolerance:
                self.remove( self.get_children()[0] )
                
                if self.get_children()[-1].maneuver_id < len(self.maneuvers)-1:
                    self.add_a_widget(i_man = self.get_children()[-1].maneuver_id + 1)
                
                self.search_index_range = self.get_search_range(i_maneuver = self.get_children()[0].maneuver_id, overlap_distance = 200 )
                
                
            else:
                air_dist_to_next = helpers.angles.haversine_distance(lat1_deg=route_lats_deg[i_closest_segment+1], 
                                                                     lon1_deg=route_lons_deg[i_closest_segment+1],
                                                                     lat2_deg=lat_deg, 
                                                                     lon2_deg=lon_deg)

                dist = route_dists_from_start[ route_i_man ] - route_dists_from_start[ i_closest_segment+1 ] + air_dist_to_next
                dist_blocks = helpers.round.distance_to_rounded_textblocks(dist)
                text = self.maneuvers[man_id]["text_blocks"]["distance_preposition"] + " " + dist_blocks["distance"] + " " + dist_blocks["distance_unit_abbrev"]
                self.get_children()[0].set_top_text( text )
    