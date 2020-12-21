#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
This file defines route provider.
A route provider finds a set of roads, leading from a start location to a destination.
"""

import numpy as np

import helpers.download
import helpers.angles


def get_mapping_of_names_to_classes():
    """
    @brief: Pointers to all classes that shall be usable.
    
    @return d (dict)
    """
    d = {"Router": Router,
        "OSRM": OSRM,
        "OSM_Scout": OSM_Scout,
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
        self.lat_deg = []
        self.lon_deg = []
        self.maneuvers = []
        self.dist_from_start = []
        
    def get_polyline_of_whole_route(self, color_rgba = (0,0,1,0.5) ):
        return {"lat_deg":self.lat_deg,"lon_deg":self.lon_deg, "color_rgba": color_rgba}
    


class OSRM(Router):    
    def set_route(self, waypoints):
 
        waypoints_as_str = ";".join( list(",".join(point) for point in np.array(waypoints, dtype=str) ) )
        url = self.url_template.replace("{waypoints}", waypoints_as_str)
        d = helpers.download.remote_json_to_py(url=url)
        
        if d["code"].upper() != "OK":
            raise Exception(d["code"])
        
        self.route = d["routes"][0]
        
        icon_types = {"arrive":"arrive",
           "continue"        :"crossing",
           "straight"        :"crossing",
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
           "roundabout turn" :"crossing",
           "exit roundabout" :"crossing",
            }
        
        self.__set_maneuvers(route = self.route, icon_types = icon_types)
        
        
    def __set_maneuvers(self, route, icon_types):    

        # First shot: every OSRM step is exactly one maneuver.
        # TODO: Rotary entry and exit are 2 separate steps. 
        #       Both, entry and exit, are represented by a 3-way crossing (rotary, rotary, exit).
        #       Better: combine (all intersections of the entry step) and (the first intersection of the exit step) to one big icon.
        # TODO: Notifications are a maneuver. Let's check whether this is a good choice in practice.
        # TODO: use different icon types for roundabouts
        # TODO: use different icon type for U-Turn

        self.lat_deg = []
        self.lon_deg = []
        self.maneuvers = []
            
        if"legs" in route:
            for leg in route["legs"]:
                for step in leg["steps"]:
                    maneuver_ind =  max( 0, len(self.lat_deg)-1 )

                    coords = np.array(step["geometry"]["coordinates"])
                    self.lat_deg = np.hstack([self.lat_deg, coords[:,1]])
                    self.lon_deg = np.hstack([self.lon_deg, coords[:,0]])
                       

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
                    
                    self.maneuvers += [{
                       "location"            : step["intersections"][0]["location"],
                       "bearings_deg"        : np.array(bearings_deg),
                       "in_bearing_deg"      : in_bearing_deg,
                       "out_bearing_deg"     : out_bearing_deg,
                       "icon_type"           : icon_types[ typ ],
                       "left_driving"        : ( step["driving_side"].upper() == "LEFT" ),
                       "type"                : typ,
                       "street_name_after"   : step["name"],
                       "movement_modifier"   : modifier,
                       "exit_number"         : exit_number,
                       "ind_on_route"        : maneuver_ind,
                       "distance_to_next"    : step["distance"],
                        }]

        # calculate the road distance from the start
        delta = helpers.angles.haversine_distance(lat1_deg = self.lat_deg[:-1], 
                                                  lon1_deg = self.lon_deg[:-1], 
                                                  lat2_deg = self.lat_deg[1:], 
                                                  lon2_deg = self.lon_deg[1:])
        self.dist_from_start = np.hstack( [[0], np.cumsum(delta)] )
        
        # add distance to previous
        self.maneuvers[0]["distance_to_prev"] = 0
        for i_man in np.arange(len(self.maneuvers)-1)+1:
            self.maneuvers[i_man]["distance_to_prev"] = self.maneuvers[i_man-1]["distance_to_next"]

        # add whole route to each maneuver
        # (Python uses lazy copy, so RAM is occupied only once)
        for i_man in np.arange(len(self.maneuvers)):
            self.maneuvers[i_man]["route_lat_deg"]              = self.lat_deg
            self.maneuvers[i_man]["route_lon_deg"]              = self.lon_deg
            self.maneuvers[i_man]["distances_from_route_start"] = self.dist_from_start


class OSM_Scout(Router):    
    def set_route(self, waypoints):
        locs = []
        for point in np.array(waypoints):
            locs += ["{\"lat\":" + str(point[1]) + ", \"lon\":" + str(point[0]) +"}"]
        locations = "\"locations\": [" + ", ".join(locs) + "]"
        
        # TODO: allow further options
        
        # "costing": "auto", 
        # "costing_options": {"auto": {"use_ferry": 0.5, "use_highways": 1, "use_tolls": 0.5}}, 
        # "directions_options": {"language": "en", "units": "kilometers"}}
        
        json_str = "json= {" + locations + "}"
        json_str = helpers.download.encode_special_characters( json_str )

        url = self.url_template.replace("{json}", json_str)

        d = helpers.download.remote_json_to_py(url=url)
        
        print(d)
        import json
        f = open("valhalla_result.json", "w")
        json.dump(d, f)
        f.close()
        
        raise NotImplementedError("TODO: implement analysis of server response")
        self.maneuvers = []