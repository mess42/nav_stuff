#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import numpy as np

import providers.download_helpers
#import calc.angles


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
        nth = "1st"
    elif n == 2:
        nth == "2nd"
    elif n == 3:
        nth = "3rd"
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
            self.trip = self.set_trip(waypoints)

    def set_trip(self, waypoints):
        """
        @brief: Store the waypoints and pre-compute the routing.
        
        @param waypoints: (2d numpy array of Nx2 float)
             Longitudes and latitudes of 
             trip start, intermediate points, and final destination.
             Intermediate points are optional. 
             Use intermediate points if you wish to go via a certain location,
             or for a round trip with start equal to final destination.
             waypoints[:,0] are longitudes
             waypoints[:,1] are latitudes
        """
        pass

    def get_polyline_of_whole_trip(self):
        return {"lat_deg":[], "lon_deg":[]}


class OSRM(Router):    
    def set_trip(self, waypoints):

        waypoints_as_str = ";".join( list( ",".join(point) for point in np.array(waypoints, dtype=str) ) )
        url = self.url_template.replace("{waypoints}", waypoints_as_str)
        d = providers.download_helpers.remote_json_to_py(url=url)
        
        if d["code"].upper() != "OK":
            raise Exception(d["code"])
        
        self.trip = d["trips"][0]

    def get_polyline_of_whole_trip(self):

        lat_deg = []
        lon_deg = []
        if ("geometry" in self.trip) and ("coordinates" in self.trip["geometry"]):
            lonlats = np.array(self.trip["geometry"]["coordinates"])
            lat_deg = lonlats[:,1]
            lon_deg = lonlats[:,0]
        
        return {"lat_deg":lat_deg, "lon_deg":lon_deg}


"""
    def step_to_text(self, step):
            
        osrm_texter = {
            "arrive"     : "arrive at {name}",
            "continue"   : "{modifier}. Continue on {name}",
            "depart"     : "depart {nesw_after} to {name}",
            "end of road": "{modifier}. To {name}",
            "exit rotary": "{exit_number} exit. To {name}",
            "new name"   : "{modifier}. Continue to {name}",
            "turn"       : "{modifier}. To {name}",
            }
    
        
        merge 	merge onto a street (e.g. getting on the highway from a ramp, the modifier specifies the direction of the merge )
        on ramp 	take a ramp to enter a highway (direction given my modifier )
        off ramp 	take a ramp to exit a highway (direction given my modifier )
        fork 	take the left/right side at a fork depending on modifier
        roundabout 	traverse roundabout, if the route leaves the roundabout there will be an additional property exit for exit counting. The modifier specifies the direction of entering the roundabout.
        rotary 	a traffic circle. While very similar to a larger version of a roundabout, it does not necessarily follow roundabout rules for right of way. It can offer rotary_name and/or rotary_pronunciation parameters (located in the RouteStep object) in addition to the exit parameter (located on the StepManeuver object).
        roundabout turn 	Describes a turn at a small roundabout that should be treated as normal turn. The modifier indicates the turn direciton. Example instruction: At the roundabout turn left .
        notification 	not an actual turn but a change in the driving conditions. For example the travel mode or classes. If the road takes a turn itself, the modifier describes the direction
        exit roundabout 	Describes a maneuver exiting a roundabout (usually preceeded by a roundabout instruction)
    
        text_replacement_dict = {
            "{name}"       : step["name"],
            "{modifier}"   : "".join(list(man["modifier"] for man in [step["maneuver"]] if "modifier" in man )),
            "{exit_number}": "".join(list(ordinal(man["exit"]) for man in [step["maneuver"]] if "exit" in man)) ,
            "{nesw_after}": calc.angles.azimuth_to_nesw_string(step["maneuver"]["bearing_after"])
            }
        
        if step["maneuver"]["type"] not in osrm_texter:
            # TODO: implement all maneuver types
            # TODO: remove this branch once the API is fully implemented, or decide to keep it
            print("TODO: implement step = ", step)
            txt = "TODO: implement " + step["maneuver"]["type"]
        else:            
            txt = osrm_texter[step["maneuver"]["type"]]
            for key in text_replacement_dict:
                txt = txt.replace( key, text_replacement_dict[key] )        
        return txt
"""



if __name__ == "__main__":

    waypoints = np.array([[13.388860,52.517037],[13.397634,52.529407],[13.428555,52.523219],[13.418555,52.523215]])

    router = OSRM( url_template= "https://router.project-osrm.org/trip/v1/driving/{waypoints}?source=first&destination=last&steps=true&geometries=geojson")    
    router.set_trip(waypoints)
    
    lats_deg, lons_deg = router.get_polyline_of_whole_trip()
    
"""        
    for leg in trip["legs"]:
        for step in leg["steps"]:
            
            line_from_maneuver_to_next_one = np.array(step["geometry"]["coordinates"])
            
            maneuver_loc = step["maneuver"]["location"]
            
            step_as_text = router.step_to_text(step)
            
            print(step_as_text, "and continue", step["distance"], "m")
"""         