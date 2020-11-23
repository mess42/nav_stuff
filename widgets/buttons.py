#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

class ResultButton(Gtk.Button):
    def __init__(self, label, result):
        Gtk.Button.__init__(self)
        self.set_label( label )
        self.set_alignment(0,0)
        self.result = result

class ApplySettingsButton(Gtk.Button):
    def __init__(self, label, dropdown_menus_to_oversee={} ):
        Gtk.Button.__init__(self)
        self.set_label( label )
        #self.set_alignment(0,0)
        self.dropdown_menus_to_oversee = dropdown_menus_to_oversee
        
class SearchButton(Gtk.Button):
    def __init__(self, entry, icon_size):
        Gtk.Button.__init__(self)
        img = Gtk.Image.new_from_icon_name(Gtk.STOCK_FIND, icon_size)
        self.set_image(img)
        self.entry = entry
    
    def get_text(self):
        return self.entry.get_text()