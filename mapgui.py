#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gdk, GLib, GdkPixbuf

import json

import providers.maps
import providers.positions
import widgets.marker_layer
import widgets.map_layer

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
        
        # Create widgets and auto-update them
        self.create_widgets()
        self.timeout_id = GLib.timeout_add(update_delay_in_ms, self.on_timeout, None)


    def create_widgets(self):
        # Global window initialisation
        self.set_title("Map Demo")
        self.set_border_width(0)
        self.maximize()

        # Create Map Canvas
        self.canvas = Gtk.Overlay().new()

        # Create Map (background layer) and Markers (Overlay on map)
        self.map_layer = widgets.map_layer.MapLayerWidget()
        self.canvas.add(self.map_layer)
        self.marker_layer = widgets.marker_layer.MarkerLayerWidget(map_copyright = self.map.map_copyright)
        self.canvas.add_overlay(self.marker_layer)

        # The Button layer contains a lot of interactive elements,
        # so let's create every element explicitly here
        self.button_layer = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.canvas.add_overlay(self.button_layer)

        self.entry = Gtk.Entry()
        self.entry.set_text("Hello World")
        self.entry.connect("activate", self.on_search_activated)
        #self.entry.override_background_color(Gtk.StateFlags.NORMAL, Gdk.RGBA(1,1,1,.9))
        self.button_layer.add(self.entry)
        

        # pack/grid widgets
        grid = Gtk.Grid()
        self.add(grid)
        grid.add(self.canvas)

        
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
        text = entry.get_text()
        print("Let's search for", text)
          
    def on_timeout(self, data):
        self.position.update_position()
        
        window_size = self.get_size()
        map_width  = window_size[0]
        map_height = window_size[1]

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
        
        
if __name__ == "__main__":
    win = MapWindow()
    win.show_all()
    Gtk.main()