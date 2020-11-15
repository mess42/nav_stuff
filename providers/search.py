#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import providers.download_helpers
import urllib.parse

class SearchProvider(object):
    def find(self, query):
        raise NotImplementedError()

class Nominatim(SearchProvider):
    def __init__(self, url_template):
        self.url_template = url_template
        
    def find(self, query):
        query = urllib.parse.quote(query) # encode special characters, URL style
        url = self.url_template.replace("{query}", query)
        search_results = providers.download_helpers.remote_json_to_py(url)
        return search_results
    
    
if __name__ == "__main__":
    
    s = Nominatim(url_template = "https://nominatim.openstreetmap.org/search/{query}?format=json")

    results = s.find("London")
    
    for r in results:
        print(r["display_name"], r["lat"], r["lon"])
    
    