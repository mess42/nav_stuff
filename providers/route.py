#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
This file defines route provider.
A route provider finds a set of roads, leading from a start location to a destination.
"""

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


class Router(object):
    def __init__(self, url_template= "", waypoints=[]):
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
        return {"lat_deg":[],"lon_deg":[]}
    
    def get_maneuver_data(self):
        return []


class OSRM(Router):    
    def set_route(self, waypoints):

        waypoints_as_str = ";".join( list(",".join(point) for point in np.array(waypoints, dtype=str) ) )
        url = self.url_template.replace("{waypoints}", waypoints_as_str)
        d = providers.download_helpers.remote_json_to_py(url=url)
        
        if d["code"].upper() != "OK":
            raise Exception(d["code"])
        
        self.route = d["routes"][0]
        
        
    def get_polyline_of_whole_route(self):

        lat_deg = []
        lon_deg = []
            
        if"legs" in self.route:
            for leg in self.route["legs"]:
                for step in leg["steps"]:
                    coords = np.array(step["geometry"]["coordinates"])
                    lat_deg = np.hstack([lat_deg, coords[:,1]])
                    lon_deg = np.hstack([lon_deg, coords[:,0]])
        
        return {"lat_deg":lat_deg,"lon_deg":lon_deg}


    def get_maneuver_data(self):
        
        # First shot: every OSRM step is exactly one maneuver.
        # TODO: Rotary entry and exit are 2 separate steps. 
        #       Both, entry and exit, are represented by a 3-way crossing (rotary, rotary, exit).
        #       Better: combine (all intersections of the entry step) and (the first intersection of the exit step) to one big icon.
        # TODO: Notifications are a maneuver. Let's check whether this is a good choice in practice.
        # TODO: use different icon types for roundabouts
        # TODO: use different icon type for U-Turn
        
        icon_types = {"arrive":"arrive",
           "continue"        :"crossing",
           "depart"          :"nesw_arrow",
           "end of road"     :"crossing",
           "exit rotary"     :"crossing",
           "new name"        :"crossing",
           "turn"            :"crossing",
           "fork"            :"crossing",
           "merge"           :"crossing",
           "on ramp"         :"crossing",
           "off ramp"        :"crossing",
           "roundabout"      :"crossing",
           "rotary"          :"crossing",
           "notification"    :"notification",
           "roundabout turn" : 	"crossing",
           "exit roundabout" :"crossing",
            }
        
        maneuvers = []
        if"legs" in self.route:
            for leg in self.route["legs"]:
                for step in leg["steps"]:
                    geo_before = []
                    dist_before = 0
                    if len(maneuvers) != 0:
                        # the geometry before this maneuver is the geometry after the last one
                        geo_before  = maneuvers[-1]["geometry_after"]
                        dist_before = maneuvers[-1]["distance_after"]

                    typ = step["maneuver"]["type"]

                    modifier = ""
                    if "modifier" in step["maneuver"]:
                        modifier = step["maneuver"]["modifier"]
                        if modifier == "uturn":
                            typ = "uturn"
                        if typ == "turn" and modifier == "straight":
                            typ = "straight"
                
                    bearings_deg = step["intersections"][0]["bearings"]

                    in_bearing_deg = float("nan")
                    if "in" in step["intersections"][0]:
                        in_bearing_deg = bearings_deg[ step["intersections"][0]["in"] ]

                    out_bearing_deg = float("nan")
                    if "out" in step["intersections"][0]:
                        out_bearing_deg = bearings_deg[ step["intersections"][0]["out"] ]

                    exit_number = 0
                    if "exit" in step["maneuver"]:
                        exit_number = step["maneuver"]["exit"]
                    
                    maneuver = {
                       "location"          : step["intersections"][0]["location"],
                       "bearings_deg"      : bearings_deg,
                       "in_bearing_deg"    : in_bearing_deg,
                       "out_bearing_deg"   : out_bearing_deg,
                       "icon_type"         : icon_types[ typ ],
                       "left_driving"      : ( step["driving_side"].upper() == "LEFT" ),
                       "type"              : typ,
                       "street_name_after" : step["name"],
                       "movement_modifier" : modifier,
                       "exit_number"       : exit_number,
                       "geometry_before"   : geo_before,
                       "geometry_after"    : step["geometry"]["coordinates"],
                       "distance_before"   : dist_before,
                       "distance_after"    : step["distance"]
                        }
                    
                    maneuvers += [ maneuver ]

        return maneuvers