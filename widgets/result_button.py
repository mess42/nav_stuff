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


