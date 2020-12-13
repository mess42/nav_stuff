#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import numpy as np

import providers.download_helpers
import calc.angles


def get_mapping_of_names_to_classes():
    """
    @brief: Pointers to all classes that shall be usable.
    
    @return d (dict)
    """
    d = {"Router": Router,
         "OSRM": OSRM
        }
    return d


def ordinal(n):
    nth = ""
    if n == 1:
        nth = "first"
    elif n == 2:
        nth = "second"
    elif n == 3:
        nth = "third"
    else:
        nth = str(n) + "th"
    # there shouldn't be a roundabout with more than 20 exits
    return nth


class Router(object):
    def __init__(self, url_template="", waypoints=[]):
        """
        @brief: A router that connects start an destination by a series of roads and turns.
            This is a baseclass that provides all methods, but does not do anything.
            Use if you wish no routing.
        
        @param url_template (str)
            URL to catch the route from, either localhost or an online provider.
            All parameters (like vehicle type, shortest or fastest) should
            be hardcoded in the URL, except for waypoints.
            The place where waypoints should be inserted shall be marked by
            the string '{waypoints}'.
        @param waypoints (numpy array)
            If not empty, a trip will be generated.
            See self.set_trip for details.
        """
        self.url_template = url_template
        self.waypoints = waypoints
        self.trip = {}
        if len(self.waypoints) != 0:
            self.route = self.set_route(waypoints)

    def set_route(self, waypoints):
        """
        @brief: Store the waypoints and pre-compute the routing.
        
        @param waypoints: (2d numpy array of Nx2 float)
             Longitudes and latitudes of 
             route start, intermediate points, and final destination.
             Intermediate points are optional. 
             Use intermediate points if you wish to go via a certain location,
             or for a round trip with start equal to final destination.
             waypoints[:,0] are longitudes
             waypoints[:,1] are latitudes
        """
        pass

    def get_polyline_of_whole_route(self):
        return {"lat_deg":[], "lon_deg":[]}


class OSRM(Router):    
    def set_route(self, waypoints):

        waypoints_as_str = ";".join( list( ",".join(point) for point in np.array(waypoints, dtype=str) ) )
        url = self.url_template.replace("{waypoints}", waypoints_as_str)
        d = providers.download_helpers.remote_json_to_py(url=url)
        
        if d["code"].upper() != "OK":
            raise Exception(d["code"])
        
        self.route = d["routes"][0]
        
        # Dirty routing test
        last_dist = 0
        for leg in self.route["legs"]:
            for step in leg["steps"]:
                blocks = self.__step_to_text_blocks( step, distance_in_m = last_dist)
                last_dist = step["distance"]
                
                msg  = blocks["distance_preposition"]
                msg += blocks["distance"]
                msg += blocks["distance_unit_abbrev"]
                msg += blocks["verb"]
                msg += blocks["verb_modifier"]
                msg += blocks["to_preposition"]
                msg += blocks["new_name"]
                
                print(msg)
        # end of dirty routing test
        
        
    def get_polyline_of_whole_route(self):

        lat_deg = []
        lon_deg = []
            
        if "legs" in self.route:
            for leg in self.route["legs"]:
                for step in leg["steps"]:
                    coords = np.array(step["geometry"]["coordinates"])
                    lat_deg = np.hstack([lat_deg, coords[:,1]])
                    lon_deg = np.hstack([lon_deg, coords[:,0]])
        
        return {"lat_deg":lat_deg, "lon_deg":lon_deg}


    def __step_to_text_blocks(self, step, distance_in_m = None):

        verbs = {
            "arrive"     : "arrive ",
            "continue"   : "continue ",
            "depart"     : "depart ",
            "end of road": "at the end of the road, turn ",
            "exit rotary": "take the ",
            "new name"   : "continue ",
            "turn"       : "turn ",
            "fork"       : "fork ",
            "merge"      : "merge ",
            "on ramp"    : "take the ramp to the ",
            "off ramp"   : "take the ramp on the ",
            "roundabout" : "enter the ",
            "rotary"     : "enter the ",
            "roundabout turn" : 	"at the roundabout, turn ",
            "exit roundabout": "take the ",
            }
            
        modifiers = {            
            "arrive"     : "",
            "continue"   : "{modifier} ",
            "depart"     : "{nesw_after} ",
            "end of road": "{modifier} ",
            "exit rotary": "{exit_number} exit ",
            "new name"   : "{modifier} ",
            "turn"       : "{modifier} ",
            "fork"       : "{modifier} ",
            "merge"      : "",
            "on ramp"    : "{modifier} ",
            "off ramp"   : "{modifier} to exit ",
            "roundabout" : "roundabout ",
            "rotary"     : "rotary ",
            "roundabout turn" : 	"{modifier} ",
            "exit roundabout": "{exit_number} exit ",
            }
        
        to_prepositions = {
            "arrive"     : "at ",
            "continue"   : "on ",
            "depart"     : "to ",
            "end of road": "to ",
            "exit rotary": "to ",
            "new name"   : "to ",
            "turn"       : "to ",
            "fork"       : "to ",
            "merge"      : "on ",
            "on ramp"    : "onto ",
            "off ramp"   : "to ",
            "roundabout" : "",
            "rotary"     : "",
            "roundabout turn" : 	"to ",
            "exit roundabout": "to ",
            }
        
        new_names = {
            "arrive"     : "{name}",
            "continue"   : "{name}",
            "depart"     : "{name}",
            "end of road": "{name}",
            "exit rotary": "{name}",
            "new name"   : "{name}",
            "turn"       : "{name}",
            "fork"       : "{name}",
            "merge"      : "{name}",
            "on ramp"    : "{name}",
            "off ramp"   : "{name}",
            "roundabout" : "",
            "rotary"     : "",
            "roundabout turn" : 	"{name}",
            "exit roundabout": "{name}",
            }
        
        text_replacement_dict = {
            "{name}"       : step["name"],
            "{modifier}"   : "".join(list(man["modifier"] for man in [step["maneuver"]] if "modifier" in man )),
            "{exit_number}": "".join(list(ordinal(man["exit"]) for man in [step["maneuver"]] if "exit" in man)) ,
            "{nesw_after}": calc.angles.azimuth_to_nesw_string(step["maneuver"]["bearing_after"])
            }
        
        typ = step["maneuver"]["type"]
        if typ not in verbs:
            print(step)
            raise Exception( "TODO: implement " + step["maneuver"]["type"] )

        blocks = {"distance_preposition": "",
                  "distance": "",
                  "distance_unit": "",
                  "distance_unit_abbrev": "",
                  "verb": verbs[typ],
                  "verb_modifier": modifiers[typ],
                  "to_preposition": to_prepositions[typ],
                  "new_name": new_names[typ]
                 }
                  
        if distance_in_m is not None and typ not in ["exit roundabout", "exit rotary"]:
            if distance_in_m >= 0:
                if distance_in_m < 20:
                    blocks["distance_preposition"] = "now "
                    blocks["distance"] = ""
                    blocks["distance_unit"] = ""
                    blocks["distance_unit_abbrev"] = ""
                elif distance_in_m < 200:
                    blocks["distance_preposition"] = "in "
                    blocks["distance"] = str( int(np.round(distance_in_m,-1)) )
                    blocks["distance_unit"] = " meters "
                    blocks["distance_unit_abbrev"] = " m "
                elif distance_in_m < 1000:
                    blocks["distance_preposition"] = "in "
                    blocks["distance"] = str( int(np.round(distance_in_m,-2)) )
                    blocks["distance_unit"] = " meters "
                    blocks["distance_unit_abbrev"] = " m "
                elif distance_in_m < 20000:
                    blocks["distance_preposition"] = "in "
                    blocks["distance"] = str( np.round(distance_in_m/1000,1) )
                    blocks["distance_unit"] = " kilometers "
                    blocks["distance_unit_abbrev"] = " km "
                    if blocks["distance"] == 1:
                        blocks["distance_unit"] = " kilometer "                        
                elif distance_in_m < 100000:
                    blocks["distance_preposition"] = "in "
                    blocks["distance"] = str( int(np.round(distance_in_m/1000)) )
                    blocks["distance_unit"] = " kilometers "
                    blocks["distance_unit_abbrev"] = " km "
                else:
                    blocks["distance_preposition"] = "in "
                    blocks["distance"] = str( int(np.round(distance_in_m/1000,-1)) )
                    blocks["distance_unit"] = " kilometers "
                    blocks["distance_unit_abbrev"] = " km "

        for block_name in blocks:
            for key in text_replacement_dict:
                blocks[block_name] = blocks[block_name].replace( key, text_replacement_dict[key] )        
        
        # Corrections
        if blocks["verb_modifier"] == "uturn":
            blocks["verb"] = "make a "
        if blocks["new_name"] == "":
            blocks["to_preposition"] = ""
        if blocks["verb"] == "turn " and blocks["verb_modifier"] == "straight":
            blocks["verb"] = "continue "
                  
        return blocks




if __name__ == "__main__":

    waypoints = np.array([[13.388860,52.517037],[13.397634,52.529407],[13.428555,52.523219],[13.418555,52.523215]])

    router = OSRM( url_template= "https://router.project-osrm.org/trip/v1/driving/{waypoints}?source=first&destination=last&steps=true&geometries=geojson")    
    router.set_route(waypoints)
    
    lats_deg, lons_deg = router.get_polyline_of_whole_route()
    
"""        
    for leg in trip["legs"]:
        for step in leg["steps"]:
            
            line_from_maneuver_to_next_one = np.array(step["geometry"]["coordinates"])
            
            maneuver_loc = step["maneuver"]["location"]
            
            step_as_text = router.step_to_text(step)
            
            print(step_as_text, "and continue", step["distance"], "m")
"""         