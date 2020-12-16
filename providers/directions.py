#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
This file defines direction providers.
A direction provider converts a route to message signs and speech.
"""

import calc.angles
import widgets.direction_icons

def get_mapping_of_names_to_classes():
    """
    @brief: Pointers to all classes that shall be usable.
    
    @return d (dict)
    """
    d = {
        "Director": Director,
        "CarDirector": CarDirector,
        }
    return d


def english_dicts():
    verbs = {
       "arrive"     :"arrive",
       "continue"   :"turn",
       "straight"   :"continue",
       "depart"     :"depart",
       "end of road":"at the end of the road, turn",
       "exit rotary":"take the",
       "new name"   :"continue",
       "turn"       :"turn",
       "fork"       :"fork",
       "merge"      :"merge",
       "on ramp"    :"take the ramp to the",
       "off ramp"   :"take the ramp on the",
       "roundabout" :"enter the",
       "rotary"     :"enter the",
       "roundabout turn" : 	"at the roundabout, turn",
       "exit roundabout":"take the",
        }
        
    modifiers = {            
       "arrive"     :"",
       "continue"   :"{movement_modifier}",
       "straight"   :"{movement_modifier}",
       "depart"     :"{nesw_after}",
       "end of road":"{movement_modifier}",
       "exit rotary":"{exit_number} exit",
       "new name"   :"{movement_modifier}",
       "turn"       :"{movement_modifier}",
       "fork"       :"{movement_modifier}",
       "merge"      :"",
       "on ramp"    :"{movement_modifier}",
       "off ramp"   :"{movement_modifier} and exit",
       "roundabout" :"roundabout",
       "rotary"     :"rotary",
       "roundabout turn" : 	"{movement_modifier}",
       "exit roundabout":"{exit_number} exit",
        }
    
    modifiers2 = {
        "uturn": "U-turn",
        "sharp right"  : "sharp right",
        "right"        : "right",
        "slight right" : "slight right",
        "straight"     : "straight",
        "slight left"  : "slight left",
        "left"         : "left",
        "sharp left"   : "sharp left",    
        }
    
    to_prepositions = {
       "arrive"          : "at",
       "continue"        : "to",
       "straight"        : "to",
       "depart"          : "to",
       "end of road"     : "to",
       "new name"        : "to",
       "turn"            : "to",
       "fork"            : "to",
       "merge"           : "on",
       "on ramp"         : "onto",
       "off ramp"        : "to",
       "roundabout"      : "",
       "exit roundabout" : "to",
       "roundabout turn" : "to",
       "rotary"          : "",
       "exit rotary"     : "to",
        }
    
    street_name_after = {
       "arrive"     :"{street_name_after}",
       "continue"   :"{street_name_after}",
       "straight"   :"{street_name_after}",
       "depart"     :"{street_name_after}",
       "end of road":"{street_name_after}",
       "exit rotary":"{street_name_after}",
       "new name"   :"{street_name_after}",
       "turn"       :"{street_name_after}",
       "fork"       :"{street_name_after}",
       "merge"      :"{street_name_after}",
       "on ramp"    :"{street_name_after}",
       "off ramp"   :"{street_name_after}",
       "roundabout" :"",
       "rotary"     :"",
       "roundabout turn" : 	"{street_name_after}",
       "exit roundabout":"{street_name_after}",
        }
    
    ordinals = {
       0:  "None",
       1:  "first",
       2:  "second",
       3:  "third",
       4:  "4th",
       5:  "5th",
       6:  "6th",
       7:  "7th",
       8:  "8th",
       9:  "9th",
       10: "10th"
       }
    
    dicts = { "verbs"            : verbs, 
              "modifiers"        : modifiers, 
              "modifiers2"       : modifiers2,
              "to_prepositions"  : to_prepositions, 
              "street_name_after": street_name_after,
              "ordinals"         : ordinals
            }
    
    return dicts


class Director(object):
    def __init__(self, language_dicts = english_dicts() ):
        """
        @param maneuvers (list of dicts)
        @param language_dicts (dict of dicts)
        
        # TODO: param language as str. The dicts are created based on that str. The profile definitions can set the language str.
        """
        self.language_dicts = language_dicts
        self.maneuvers = []
    
    def set_data(self, maneuvers):
        pass # base class does not do anything
    
    def get_icon_class_by_name(self,name):
        d = { "arrive"       : widgets.direction_icons.CheckerFlag,
              "crossing"     : widgets.direction_icons.Crossing,
              "nesw_arrow"   : widgets.direction_icons.NESWArrow,
              "notification" : widgets.direction_icons.Notification,
            }
        return d[name]
    
    def maneuver_to_text_blocks(self, maneuver):        

        # get the first draft        
        typ = maneuver["type"]
        blocks = {"verb": self.language_dicts["verbs"][typ],
                 "verb_modifier": self.language_dicts["modifiers"][typ],
                 "to_preposition": self.language_dicts["to_prepositions"][typ],
                 "street_name_after": self.language_dicts["street_name_after"][typ]
                 }

        # replace {variables} by maneuver data
        text_replacement_dict = {
           "{street_name_after}": maneuver["street_name_after"],
           "{movement_modifier}": "{" + maneuver["movement_modifier"] +"}",
           "{exit_number}"      : self.language_dicts["ordinals"][maneuver["exit_number"]],
           "{nesw_after}"       : calc.angles.azimuth_to_nesw_string( azim_deg = maneuver["out_bearing_deg"] )
            }
        for key in self.language_dicts["modifiers2"]:
            text_replacement_dict["{"+ key + "}"] = self.language_dicts["modifiers2"][key]
            
        for block_name in blocks:
            for key in text_replacement_dict:
                blocks[block_name] = blocks[block_name].replace( key, text_replacement_dict[key] )        
        
        # do the final polishing
        if blocks["street_name_after"] == "":
            blocks["to_preposition"] = ""
    
        return blocks


class CarDirector(Director):
    def set_data(self, maneuvers):
        self.maneuvers = maneuvers
        
        for maneuver in self.maneuvers:
            maneuver["text_blocks"] = self.maneuver_to_text_blocks(maneuver)
            
            IconClass = self.get_icon_class_by_name( maneuver["icon_type"] )
            maneuver["icon_object"] = IconClass(in_bearing_deg  = maneuver["in_bearing_deg"], 
                                                out_bearing_deg = maneuver["out_bearing_deg"], 
                                                bearings_deg    = maneuver["bearings_deg"], 
                                                size            = 120, 
                                                left_driving    = maneuver["left_driving"],
                                                )
            
            # TODO: remove the print section once proper directions are established.            
            s = list( maneuver["text_blocks"][key] for key in maneuver["text_blocks"])
            s = " ".join(s)
            print(s)

