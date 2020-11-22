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
import providers.route
import widgets.marker_layer
import widgets.map_layer
import widgets.buttons
import calc.angles

class MapWindow(Gtk.Window):
    def __init__(self, 
        profiles_filename  = "profile_definitions.json", 
        settings_filename    = "settings.json", 
        update_delay_in_ms = 50
        ):

        Gtk.Window.__init__(self)
        self.connect("destroy", self.on_destroy)
        
        # Load Configuration files
        self.profiles = self.json2dict(profiles_filename)
        self.settings   = self.json2dict(settings_filename)
        self.settings_have_changed = False

        # providers for map, position, search, and routing
        
        self.providers = {}
        for provider_type in self.profiles:
            self.providers[provider_type] = self.make_provider_object( provider_type = provider_type, settings = self.settings, profiles = self.profiles, provider_dict = self.collect_available_provider_classes()[provider_type] )
        
        # Create widgets and auto-update them
        self.create_widgets()
        GLib.timeout_add(update_delay_in_ms, self.on_timeout, None)


    def create_widgets(self):
        # Global window initialisation
        self.set_title("Map Demo")
        self.set_border_width(0)
        self.maximize()


        self.widgets = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        
        self.entry = Gtk.Entry()
        #self.entry.set_text("Hello World")
        self.entry.connect("activate", self.on_search_activated)
        self.widgets.add(self.entry)
        

        # Create Map Canvas
        self.canvas = Gtk.Overlay().new()
        self.widgets.add(self.canvas)

        # Create Map (background layer) 
        # and Markers (Overlay on map)
        self.map_layer = widgets.map_layer.MapLayerWidget()
        self.canvas.add(self.map_layer)
        self.marker_layer = widgets.marker_layer.MarkerLayerWidget(map_copyright = self.providers["map"].map_copyright)
        self.canvas.add_overlay(self.marker_layer)

        # Top layer is the interactive layer.
        # Clickable objects must be on the top layer,
        # so widgets of this layer are exchanged based on context.
        self.interactive_layer = Gtk.Grid()
        self.canvas.add_overlay( self.interactive_layer )
        self.make_nav_buttons( layer = self.interactive_layer )

        self.add(self.widgets)
        self.show_all()
        
    def json2dict(self, filename):
        f = open(filename,"r")
        dic = json.load(f)
        f.close()
        return dic


    def collect_available_provider_classes(self):
        p = { "map":      providers.maps.get_mapping_of_names_to_classes(),
              "position": providers.positions.get_mapping_of_names_to_classes(),
              "search":   providers.search.get_mapping_of_names_to_classes(), 
              "router":   providers.route.get_mapping_of_names_to_classes() 
            }
        return p


    def make_provider_object(self, provider_type, settings, profiles, provider_dict ):
        """
        @brief: make a map, position, or routing provider object.
        
        @param: provider_type (str)
                Map or position or router
        @param: settings (dict)
        @param: profiles (dict)
                Must contain the entry profiles[provider_type][profile_name].
                The entry is a dict with keys class_name and parameters.
        @param: provider_dict (dict)
                Mapping of class_name to a Class pointer.
        
        @return provider (object)
        """
        
        # The profile and settings.json can be edited by hand,
        # so let's do a sanity check
        if provider_type not in profiles:
            e = "Profile type \'" + str(provider_type) + "\' not found in profiles json. "
            e += "Choose one of " + str( list(profiles.keys() ))
            raise Exception(e)
        if provider_type not in settings:
            e = "Profile type \'" + str(provider_type) + "\' not found in settings json. "
            e += "Choose one of " + str( list(settings.keys() ))
            raise Exception(e)
            
        profile_name = settings[provider_type]
        
        if profile_name not in profiles[provider_type]:
            e  = "Profile name \'" + str(profile_name) + "\' "
            e += "in type \'" + str(provider_type) + "\' not found. "
            e += "Choose one of " + str( list(profiles[provider_type].keys() ))
            raise Exception(e)
        if "class_name" not in profiles[provider_type][profile_name]:
            raise Exception("class_name not found in profile " + str(provider_type) + " / " + str(profile_name) )
        if "parameters" not in profiles[provider_type][profile_name]:
            raise Exception("parameters not found in profile " + str(provider_type) + " / " + str(profile_name) )

        provider_class_name = profiles[provider_type][profile_name]["class_name"]
        params              = profiles[provider_type][profile_name]["parameters"]
        ProviderClass       = provider_dict[provider_class_name]
        provider            = ProviderClass(**params)
        return provider

    def enrich_results_with_data_rel_to_ego_pos(self,list_of_result_dicts):
        for res in list_of_result_dicts:
            airline = calc.angles.calc_properties_of_airline(
                         lat1_deg = self.providers["position"].latitude,
                         lon1_deg = self.providers["position"].longitude,
                         lat2_deg = float(res["lat"]),
                         lon2_deg = float(res["lon"])
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

        return list_of_result_dicts

    def remove_all_children(self, parent):
        for child in parent.get_children():
            parent.remove(child)


    def make_message_button(self, layer, label):

        self.remove_all_children( layer )

        msg_button = Gtk.Button.new_with_label(label)
        layer.attach( child=msg_button, left=0, top=0, width=1, height=1)

        layer.show_all()


    def make_nav_buttons(self, layer):
        
        self.remove_all_children( layer )

        zoom_in_button = Gtk.Button.new_with_label("+")
        zoom_in_button.connect("clicked", self.on_zoom_in_button_clicked)
        layer.attach( child = zoom_in_button, left=0, top=0, width=1, height=1)

        zoom_out_button = Gtk.Button.new_with_label("-")
        zoom_out_button.connect("clicked", self.on_zoom_out_button_clicked)
        layer.attach( child = zoom_out_button, left=0, top=1, width=1, height=1)
        
        settings_button = Gtk.Button.new_with_label("Settings")
        settings_button.connect("clicked", self.on_settings_button_clicked)
        layer.attach( child = settings_button, left=0, top=2, width=1, height=1)
        
        layer.show_all()


    def from_no_result_to_nav_buttons(self, button):
        
        self.make_nav_buttons(layer = self.interactive_layer )
        
        repeat = False
        return repeat


    def make_search_result_buttons(self, layer, list_of_result_dicts):
        # remove zoom controls or results from previus search
        self.remove_all_children( layer )
        
        if len(list_of_result_dicts) == 0:
            button = Gtk.Button.new_with_label("no results found.")
            button.connect("clicked", self.from_no_result_to_nav_buttons)
            layer.attach( child=button, left=0, top=0, width=1, height=1)
            
            # show "no result" only for a short time and auto-return to nav buttons
            GLib.timeout_add( 3000, self.from_no_result_to_nav_buttons, None)

            
        else:  
            # make a Button for each result
            for i in range(len(list_of_result_dicts)):
                res = list_of_result_dicts[i]
                label = str(res["display_name"]) + "\n" + str(res["rounded_distance_km"]) + " km " + res["nesw"] + " (air line)"
                button = widgets.buttons.ResultButton( label = label, result = res )
                button.connect("clicked", self.on_search_result_clicked)
                layer.attach( child=button, left=0, top=i, width=1, height=1)

        layer.show_all()


    def make_settings_menu(self, layer):
        self.remove_all_children( layer )
 
        dropdown_menus = {}
    
        provider_types = list( self.profiles.keys() )
        for i in np.arange(len(provider_types)):
            
            # Label
            label = Gtk.Label()
            label.set_text(provider_types[i])
            layer.attach(child=label, left=0, top=i+1, width=1, height=1)
            
            # Dropdown menu
            dropdown_options = list(  self.profiles[provider_types[i]].keys()  )
            previously_chosen = self.settings[provider_types[i]]
            prev_ind = dropdown_options.index(previously_chosen)
            
            dropdown_menu = Gtk.ComboBoxText()
            dropdown_menu.set_entry_text_column(0)
            #dropdown_menu.connect("changed", self.on_something_changed)
            for opt in dropdown_options:
                dropdown_menu.append_text(opt)
            dropdown_menu.set_active( prev_ind )
            layer.attach(child=dropdown_menu, left=1, top=i+1, width=1, height=1)

            dropdown_menus[provider_types[i]] = dropdown_menu
            
        cancel_button = Gtk.Button.new_with_label("Cancel")
        cancel_button.connect("clicked", self.on_settings_cancel_clicked)
        layer.attach(child = cancel_button, left=0, top=0, width=1, height=1)
        
        apply_button = widgets.buttons.ApplySettingsButton(label="OK", dropdown_menus_to_oversee = dropdown_menus)
        apply_button.connect("clicked", self.on_settings_apply_clicked)
        layer.attach(child = apply_button, left=1, top=0, width=1, height=1)

        layer.show_all()

    
    def on_settings_button_clicked(self, button):
        self.make_settings_menu( layer = self.interactive_layer )
        
        
    def on_settings_cancel_clicked(self, button):
        self.make_nav_buttons( layer = self.interactive_layer )
        
        
    def on_settings_apply_clicked(self, button):
        
        dropdown_menus = button.dropdown_menus_to_oversee
        provider_types = list( self.profiles.keys() )

        for provider_type in provider_types:
            old_setting = self.settings[provider_type]
            new_setting = dropdown_menus[provider_type].get_active_text()
            if old_setting != new_setting:
                self.make_message_button(layer = self.interactive_layer, label = "Waiting for initialisation of " + provider_type + " provider ...")
                
                self.settings[provider_type]  = new_setting
                self.providers[provider_type] = self.make_provider_object( provider_type = provider_type, settings = self.settings, profiles = self.profiles, provider_dict = self.collect_available_provider_classes()[provider_type] )
                self.settings_have_changed    = True

        self.make_nav_buttons( layer = self.interactive_layer )


    def on_search_activated(self, entry):
        
        self.make_message_button(layer = self.interactive_layer, label = "Waiting for search results ...")
        
        # request results from the search provider
        list_of_result_dicts = self.providers["search"].find( entry.get_text() )
        list_of_result_dicts = self.enrich_results_with_data_rel_to_ego_pos(list_of_result_dicts)
        
        # make a Button for each result  
        self.make_search_result_buttons(layer = self.interactive_layer, list_of_result_dicts=list_of_result_dicts)


    def on_search_result_clicked(self, button):
        
        self.make_message_button(layer = self.interactive_layer, label = "Waiting for route calculation ...")
                
        self.providers["router"].set_trip(waypoints = np.array([ [self.providers["position"].longitude, self.providers["position"].latitude],[float(button.result["lon"]), float(button.result["lat"])] ]))
        polyline = self.providers["router"].get_polyline_of_whole_trip()
        polyline["color_rgba"] = (0,0,1,.5)
        
        self.marker_layer.make_marker_list( destination    = button.result, 
                                            map_copyright  = self.providers["map"].map_copyright,
                                            trip_polylines = [polyline],
                                          )

        self.make_nav_buttons( layer = self.interactive_layer )        
        self.entry.set_text(button.result["display_name"])

                  
    def on_timeout(self, data):
        self.providers["position"].update_position()
        
        #TODO: the following map size allocation only works 
        #      if self.widgets is a vertical box (portrait mode)
        #      and if self.canvas is a direct child of self.widgets
        #      Also, this is fragile and inelegant.
        window_size = self.get_size()
        sum_of_all_widget_heights_except_map_canvas = sum( list( w.get_allocation().height for w in self.widgets.get_children() if w is not self.canvas) )
        map_width = window_size[0]
        map_height = window_size[1] - sum_of_all_widget_heights_except_map_canvas

        cropped_tile = self.providers["map"].get_cropped_tile( 
                                    xsize_px = map_width, 
                                    ysize_px = map_height, 
                                    center_lat_deg = self.providers["position"].latitude, 
                                    center_lon_deg = self.providers["position"].longitude
                                    )
        self.map_layer.update(cropped_tile)
        self.marker_layer.update(cropped_tile = cropped_tile, position = self.providers["position"] )
        
        repeat = True
        return repeat
    
    def on_zoom_in_button_clicked(self, button):
        self.providers["map"].zoom_in()

    def on_zoom_out_button_clicked(self, button):
        self.providers["map"].zoom_out()
    
    def on_destroy(self, object_to_destroy):
        """
        Actions to be performed before destroying this application.
        """
        self.providers["position"].disconnect()
        if self.settings_have_changed:
            print("settings have been changed. Someone should write the changed settings back.")
        #TODO: write (possibly modified) settings back to hard drive
        Gtk.main_quit(object_to_destroy)
    
        
if __name__ == "__main__":
    win = MapWindow()
    win.show_all()
    Gtk.main()