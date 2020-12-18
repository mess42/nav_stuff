#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
This file defines search providers.
A search provider is used to convert a text input to destination coordinates.
"""

import helpers.download
import urllib.parse

# TODO: make a new simple provider that accepts coordinate inputs and converts them to float.

def get_mapping_of_names_to_classes():
    """
    @brief: Pointers to all classes that shall be usable.
    (no base classes)
    
    @return d (dict)
    """
    d = {"Nominatim": Nominatim,
         "OSMScout" : OSMScout,
        }
    return d


class SearchProvider(object):
    def find(self, query):
        raise NotImplementedError()

class Nominatim(SearchProvider):
    def __init__(self, url_template):
        self.url_template = url_template
        
    def find(self, query):
        query = urllib.parse.quote(query) # encode special characters, URL style
        url = self.url_template.replace("{query}", query)
        search_results = helpers.download.remote_json_to_py(url)
        search_results = self.postprocessing(search_results)
        return search_results
    
    def postprocessing(self, search_results):
        return search_results

class OSMScout(Nominatim):
    def __init__(self):
        Nominatim.__init__(self, url_template = "http://localhost:8553/v1/search?limit=10&search={query}")
        
    def postprocessing(self, search_results):
        for res in search_results:
            res["lon"] = res["lng"]
            res["display_name"] = res["title"]
        return search_results

    
if __name__ == "__main__":
    
    s = Nominatim(url_template = "https://nominatim.openstreetmap.org/search/{query}?format=json")

    results = s.find("London")
    
    for r in results:
        print(r["display_name"], r["lat"], r["lon"])
    
    