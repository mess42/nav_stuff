#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, GLib

import json
import numpy as np

import providers.maps
import providers.positions
import providers.search
import widgets.marker_layer
import widgets.map_layer
import widgets.result_button
import calc.angles

class MapWindow(Gtk.Window):
    def __init__(self, 
        profiles_filename  = "profiles.json", 
        config_filename    = "config.json", 
        update_delay_in_ms = 50
        ):

        Gtk.Window.__init__(self)
        self.connect("destroy", self.on_destroy)
        
        # Load Configuration files
        profiles = self.json2dict(profiles_filename)
        config   = self.json2dict(config_filename)

        # Create Map and Position provider
        self.map      = self.make_provider_object( profile_type = "MapProviders",      profile_name = config["map_profile"], profiles = profiles, provider_dict = providers.maps.get_mapping_of_names_to_classes() )
        self.position = self.make_provider_object( profile_type = "PositionProviders", profile_name = config["pos_profile"], profiles = profiles, provider_dict = providers.positions.get_mapping_of_names_to_classes() )
        self.search   = self.make_provider_object( profile_type = "SearchProviders",   profile_name = config["search_profile"], profiles = profiles, provider_dict = providers.search.get_mapping_of_names_to_classes() )
                        
        # Create widgets and auto-update them
        self.create_widgets()
        self.timeout_id = GLib.timeout_add(update_delay_in_ms, self.on_timeout, None)


    def create_widgets(self):
        # Global window initialisation
        self.set_title("Map Demo")
        self.set_border_width(0)
        self.maximize()


        self.widgets = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        
        self.entry = Gtk.Entry()
        self.entry.set_text("Hello World")
        self.entry.connect("activate", self.on_search_activated)
        self.widgets.add(self.entry)
        

        # Create Map Canvas
        self.canvas = Gtk.Overlay().new()
        self.widgets.add(self.canvas)

        # Create Map (background layer) 
        # and Markers (Overlay on map)
        # and Search results (Overlay on markers)
        self.map_layer = widgets.map_layer.MapLayerWidget()
        self.canvas.add(self.map_layer)
        self.marker_layer = widgets.marker_layer.MarkerLayerWidget(map_copyright = self.map.map_copyright)
        self.canvas.add_overlay(self.marker_layer)
        self.result_layer = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.canvas.add_overlay(self.result_layer)

        self.add(self.widgets)
        self.show_all()
        
    def json2dict(self, filename):
        f = open(filename,"r")
        dic = json.load(f)
        f.close()
        return dic


    def make_provider_object(self, profile_type, profile_name, profiles, provider_dict ):
        """
        @brief: make a map, position, or routing provider object.
        
        @param: profile_type (str)
                Map or position or router
        @param: profile_name (str)
        @param: profiles (dict)
                Must contain the entry profiles[profile_type][profile_name].
                The entry is a dict with keys class_name and parameters.
        @param: provider_dict (dict)
                Mapping of class_name to a Class pointer.
        
        @return provider (object)
        """
        provider_class_name = profiles[profile_type][profile_name]["class_name"]
        params              = profiles[profile_type][profile_name]["parameters"]
        ProviderClass       = provider_dict[provider_class_name]
        provider            = ProviderClass(**params)
        return provider

    def on_search_activated(self, entry):
        
        # remove search results from previus search
        for child in self.result_layer.get_children():
            self.result_layer.remove(child)
        
        # request results from the search provider
        list_of_result_dicts = self.search.find( entry.get_text() )

        # make a Button for each result
        for res in list_of_result_dicts:           
            res = self.enrich_result(res)
            
            label = str(res["display_name"]) + "\n" + str(res["rounded_distance_km"]) + " km " + res["nesw"]
            button = widgets.result_button.ResultButton( label = label, result = res )
            button.connect("clicked", self.on_search_result_clicked)
            self.result_layer.add(button)

        self.result_layer.show_all()

    def on_search_result_clicked(self, button):
        
        for child in self.result_layer.get_children():
            self.result_layer.remove(child)
        
        self.entry.set_text(button.result["display_name"])
        
        self.marker_layer.make_marker_list( destination = button.result, 
                                           map_copyright= self.map.map_copyright)
                  
    def on_timeout(self, data):
        self.position.update_position()
        
        #TODO: the following map size allocation only works 
        #      if self.widgets is a vertical box (portrait mode)
        #      and if self.canvas is a direct child of self.widgets
        #      Also, this is fragile and inelegant.
        window_size = self.get_size()
        sum_of_all_widget_heights_except_map_canvas = sum( list( w.get_allocation().height for w in self.widgets.get_children() if w is not self.canvas) )
        map_width = window_size[0]
        map_height = window_size[1] - sum_of_all_widget_heights_except_map_canvas

        cropped_tile = self.map.get_cropped_tile( 
                                    xsize_px = map_width, 
                                    ysize_px = map_height, 
                                    center_lat_deg = self.position.latitude, 
                                    center_lon_deg = self.position.longitude
                                    )
        self.map_layer.update(cropped_tile)
        self.marker_layer.update(cropped_tile = cropped_tile, position = self.position )
        
        repeat = True
        return repeat
    
    def on_destroy(self, object_to_destroy):
        """
        Actions to be performed before destroying this application.
        """
        self.position.disconnect()
        print("Position provider disconnected.")
        #TODO: write (possibly modified) config back to hard drive
        Gtk.main_quit(object_to_destroy)
    
    def enrich_result(self,res):
        airline = calc.angles.calc_properties_of_airline(lat1_deg = self.position.latitude,
                                                         lon1_deg = self.position.longitude,
                                                         lat2_deg = float(res["lat"]),
                                                         lon2_deg = float(res["lon"]),
                                                         )
        res["rounded_distance_km"] = airline["distance_m"] / 1000
        if airline["distance_m"] < 10000:
            res["rounded_distance_km"] = np.round( res["rounded_distance_km"], 1)
        elif airline["distance_m"] < 100000:
            res["rounded_distance_km"] = int(np.round( res["rounded_distance_km"] ))
        elif airline["distance_m"] < 1000000:
            res["rounded_distance_km"] = int(np.round( res["rounded_distance_km"], -1))
        else:
            res["rounded_distance_km"] = int(np.round( res["rounded_distance_km"], -2))
        
        res["azimuth_deg"] = airline["azimuth_from_point_1_towards_2_deg"]
        res["nesw"]        = calc.angles.azimuth_to_nesw_string(azim_deg = airline["azimuth_from_point_1_towards_2_deg"])

        return res
        
if __name__ == "__main__":
    win = MapWindow()
    win.show_all()
    Gtk.main()