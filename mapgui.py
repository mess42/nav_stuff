#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, GLib, GdkPixbuf

import numpy as np
import json

import map_providers
import position_providers
import markers


def array_to_pixbuf(arr):
    """ 
    convert from numpy array to GdkPixbuf 
    """
    z     = arr.astype('uint8')
    h,w,c = z.shape
    assert c == 3 or c == 4
    pix = None
    if hasattr(GdkPixbuf.Pixbuf,'new_from_bytes'):
        Z = GLib.Bytes.new(z.tobytes())
        pix = GdkPixbuf.Pixbuf.new_from_bytes(Z, GdkPixbuf.Colorspace.RGB, c==4, 8, w, h, w*c)
    else:
        pix = GdkPixbuf.Pixbuf.new_from_data(z.tobytes(),  GdkPixbuf.Colorspace.RGB, c==4, 8, w, h, w*c, None, None)
    return pix

class MapWindow(Gtk.Window):
    def __init__(self, profiles_filename = "profiles.json"):
        
        # Global window initialisation
        Gtk.Window.__init__(self)
        self.connect("destroy", self.on_destroy)
        self.set_title("Map Demo")
        self.set_border_width(0)
        self.maximize()
        
        update_delay_in_ms = 50 #TODO: this is a hard coded value
        
        f = open(profiles_filename,"r")
        profiles = json.load(f)
        f.close()
        map_profile_name = "DebugMap" #TODO: this is a hard coded value. Better read from config file.
        pos_profile_name = "PositionSimulation" #TODO: this is a hard coded value

        # Create Map and Position provider
        self.map               = self.make_provider_object( profile_type = "MapProviders",      profile_name = map_profile_name, profiles = profiles, provider_dict = map_providers.get_mapping_of_names_to_classes() )
        self.position_provider = self.make_provider_object( profile_type = "PositionProviders", profile_name = pos_profile_name, profiles = profiles, provider_dict = position_providers.get_mapping_of_names_to_classes() )

        # Create Map Canvas Widget       
        self.canvas = Gtk.Overlay().new()

        # Create Map (background layer)
        self.map_layer_widget = MapLayerWidget()
        self.canvas.add(self.map_layer_widget)
                
        # Create Markers (overlay on map)
        self.marker_layer_widget = markers.MarkerLayerWidget()
        self.canvas.add_overlay(self.marker_layer_widget)

        # pack/grid widgets
        grid = Gtk.Grid()
        self.add(grid)
        grid.add(self.canvas)
        
        self.timeout_id = GLib.timeout_add(update_delay_in_ms, self.on_timeout, None)


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

          
    def on_timeout(self, data):
        self.position_provider.update_position()
        
        window_size = self.get_size()
        map_width  = window_size[0]
        map_height = window_size[1]

        cropped_tile = self.map.get_cropped_tile( 
                                    xsize_px = map_width, 
                                    ysize_px = map_height, 
                                    center_lat_deg = self.position_provider.latitude, 
                                    center_lon_deg = self.position_provider.longitude
                                    )
        self.map_layer_widget.update(cropped_tile)
        self.marker_layer_widget.update(cropped_tile = cropped_tile, latlon = [ self.position_provider.latitude, self.position_provider.longitude])
        
        repeat = True
        return repeat
    
    def on_destroy(self, object_to_destroy):
        """
        Actions to be performed before destroying this application.
        """
        self.position_provider.disconnect()
        print("Position provider disconnected.")
        #TODO: write (possibly modified) config back to hard drive
        Gtk.main_quit(object_to_destroy)
        

class MapLayerWidget(Gtk.Image):
    def update(self, cropped_tile):
        arr = cropped_tile.raster_image
        pix = array_to_pixbuf(arr)
        self.set_from_pixbuf(pix)


 
        
if __name__ == "__main__":
    win = MapWindow()
    win.show_all()
    Gtk.main()