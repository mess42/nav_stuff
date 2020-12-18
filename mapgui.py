#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gdk, GLib

import os
import json
import numpy as np

import providers.maps
import providers.positions
import providers.search
import providers.route
import providers.directions

import widgets.marker_layer
import widgets.map_layer
import widgets.buttons
import widgets.da_buttons
import widgets.maneuver_bar

import calc.angles
import calc.round

class MapWindow(Gtk.Window):
    def __init__(self, 
        profiles_filename  = "profile_definitions.json", 
        settings_filename    = "settings.json", 
        update_delay_in_ms = 50
        ):

        Gtk.Window.__init__(self)
        self.connect("destroy", self.on_destroy)
        
        # Load Configuration files
        self.profiles              = self.json2dict(profiles_filename)
        self.settings_filename     = settings_filename
        if os.path.isfile(settings_filename):
            self.settings              = self.json2dict(settings_filename)
            self.settings_have_changed = False
        else:
            self.settings = self.get_new_settings_dict(profiles=self.profiles)
            self.settings_have_changed = True
        self.auto_rotate = True

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
        self.previous_window_xsize, self.previous_window_ysize = self.get_size()


        self.widgets = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        
        hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        self.entry = Gtk.Entry()
        #self.entry.set_text("Hello World")
        self.entry.connect("activate", self.on_search_activated)
        
        # Create the top search bar
        size = Gtk.icon_size_from_name("Button")
        search_button = widgets.buttons.SearchButton(entry = self.entry, icon_size=size)
        search_button.connect("clicked", self.on_search_activated)
        
        hbox.pack_start(child = self.entry, expand=True, fill=True, padding=0)
        hbox.pack_end(  child = search_button, expand=False, fill=False, padding=0)
        self.widgets.pack_start(child = hbox, expand=False, fill=False, padding=0)
        

        # Create Map Canvas
        self.canvas = Gtk.Overlay().new()
        self.widgets.pack_start(child = self.canvas, expand=True, fill=True, padding=0)

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

        # Create the bottom maneuver bar.
        self.maneuver_bar = widgets.maneuver_bar.ManeuverBar()
        self.widgets.pack_start(child = self.maneuver_bar, expand=True, fill=True, padding=0)
        
        self.add(self.widgets)
        self.show_all()
        
    def json2dict(self, filename):
        f = open(filename,"r")
        dic = json.load(f)
        f.close()
        return dic
    
    def get_new_settings_dict(self, profiles):
        settings = {}
        for provider_type in profiles:
            s = list( profiles[provider_type].keys() )
            settings[provider_type] = s[0]
        return settings
            

    def collect_available_provider_classes(self):
        p = { "map":      providers.maps.get_mapping_of_names_to_classes(),
              "position": providers.positions.get_mapping_of_names_to_classes(),
              "search":   providers.search.get_mapping_of_names_to_classes(), 
              "router":   providers.route.get_mapping_of_names_to_classes(),
              "directions": providers.directions.get_mapping_of_names_to_classes()
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
            blocks = calc.round.distance_to_rounded_textblocks(airline["distance_m"])
            res["rounded_distance_str"] = blocks["distance"] + " " + blocks["distance_unit_abbrev"]
                        
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
        layer.set_row_spacing(10)

        zoom_in = widgets.da_buttons.ZoomIn(size=32)
        zoom_in.connect("button-press-event", self.on_zoom_in_clicked)
        layer.attach( child = zoom_in, left=0, top=0, width=1, height=1)

        zoom_out = widgets.da_buttons.ZoomOut(size=32)
        zoom_out.connect("button-press-event", self.on_zoom_out_clicked)
        layer.attach( child = zoom_out, left=0, top=1, width=1, height=1)
        
        settings = widgets.da_buttons.Settings(size=32)       
        settings.connect("button-press-event", self.on_settings_clicked)
        layer.attach( child = settings, left=0, top=2, width=1, height=1)

        self.north_arrow = widgets.da_buttons.NorthArrow(size=32)
        self.north_arrow.connect("button-press-event", self.on_north_arrow_clicked)
        layer.attach( child = self.north_arrow, left=0, top=3, width=1, height=1)
        
        layer.show_all()


    def from_no_result_to_nav_buttons(self, button):
        
        self.make_nav_buttons(layer = self.interactive_layer )
        
        repeat = False
        return repeat


    def make_search_result_buttons(self, layer, list_of_result_dicts):
        # remove zoom controls or results from previus search
        self.remove_all_children( layer )
        layer.set_row_spacing(0)

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
                label = str(res["display_name"]) + "\n" + str(res["rounded_distance_str"]) + " " + res["nesw"] + " (air line)"
                button = widgets.buttons.ResultButton( label = label, result = res )
                button.connect("clicked", self.on_search_result_clicked)
                layer.attach( child=button, left=0, top=i, width=1, height=1)

        layer.show_all()


    def make_settings_menu(self, layer):
        self.remove_all_children( layer )
        layer.set_row_spacing(0)

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
      
    
    def on_settings_clicked(self, button, event):
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
        self.providers["router"].set_route(waypoints = np.array([ [self.providers["position"].longitude, self.providers["position"].latitude],[float(button.result["lon"]), float(button.result["lat"])] ]))

        self.make_message_button(layer = self.interactive_layer, label = "Waiting for directions calculation ...")
        self.providers["directions"].set_data(router_maneuvers = self.providers["router"].get_maneuver_data() )
        
        self.maneuver_bar.set_new_route(maneuvers_with_direction_data = self.providers["directions"].maneuvers )
                    
        polylines = []
        whole_route_line = self.providers["router"].get_polyline_of_whole_route()
        whole_route_line["color_rgba"] = (0,0,1,.5)
        if len(whole_route_line["lat_deg"]) != 0:
            polylines.append(whole_route_line)
        
        self.marker_layer.make_marker_list( destination    = button.result, 
                                            map_copyright  = self.providers["map"].map_copyright,
                                            route_polylines = polylines,
                                          )

        self.make_nav_buttons( layer = self.interactive_layer )        
        self.entry.set_text(button.result["display_name"])


    def on_north_arrow_clicked(self, da, event):
        # toggle auto-rotate
        self.auto_rotate = not self.auto_rotate

                  
    def on_timeout(self, data):
        self.providers["position"].update_position()
        
        #TODO: the following map size allocation only works 
        #      if self.widgets is a vertical box (portrait mode)
        #      and if self.canvas is a direct child of self.widgets
        #      Also, this is fragile and inelegant.
        current_window_size = self.get_size()
        if current_window_size[0] != self.previous_window_xsize:
            # the window size can change for 2 reasons: 
            #    - either from a change in screen resolution (change from portrait to landscape)
            #    - or from newly created widgets, so that their sum does not fit the screen any more.
            # if the xsize changed, we assume it's a change of screen resolution and adapt the window size.
            # (Let's hope both reasons did not happen at the same time)
            # Else, all widgets have to squeeze a little.
            #
            # TODO: find out how to get the maximum size available to draw on (screen resolution minus title and menu bars)
            self.previous_window_xsize = current_window_size[0]
            self.previous_window_ysize = current_window_size[1]
                
        sum_of_all_widget_heights_except_map_canvas = sum( list( w.get_allocation().height for w in self.widgets.get_children() if w is not self.canvas) )
        map_width  = self.previous_window_xsize
        map_height = self.previous_window_ysize - sum_of_all_widget_heights_except_map_canvas # TODO: hard coded size!!!
        
        angle_rad = self.providers["position"].heading * np.pi / 180. * self.auto_rotate
        cropped_tile = self.providers["map"].get_rotated_cropped_tile( 
                                    xsize_px = map_width, 
                                    ysize_px = map_height, 
                                    center_lat_deg = self.providers["position"].latitude, 
                                    center_lon_deg = self.providers["position"].longitude,
                                    angle_rad = angle_rad
                                    )
        self.map_layer.update(cropped_tile)
        self.marker_layer.update(cropped_tile = cropped_tile, position = self.providers["position"] )
        self.north_arrow.update(north_bearing_deg = angle_rad * -180/np.pi)
        
        repeat = True
        return repeat
    
    def on_zoom_in_clicked(self, button, event):
        self.providers["map"].zoom_in()

    def on_zoom_out_clicked(self, button,event):
        self.providers["map"].zoom_out()
    
    def on_destroy(self, object_to_destroy):
        """
        Actions to be performed before destroying this application.
        """
        self.providers["position"].disconnect()

        if self.settings_have_changed:            
            f = open(self.settings_filename,"w")
            json.dump(self.settings, f)
            f.close()

        Gtk.main_quit(object_to_destroy)
    
        
if __name__ == "__main__":
    win = MapWindow()
    win.show_all()
    Gtk.main()