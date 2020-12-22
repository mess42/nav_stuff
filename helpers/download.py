#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
This file provides helper routines for server communication.
"""
from PIL import PngImagePlugin
import numpy as np
import urllib.parse
import requests
import json


class FakeFileHandle(object):
    def __init__(self, content):
        """
        @brief: object that behaves like a filehandle
        
        @param content (str or bytes)
        
        Imagine you have a string or Bytestring with the complete content
        of a file, but someone else expects a filehandle it can .read()
        
        example:
        f    = open("foo.txt", "r")
        dat  = f.read()       
        f2   = FakeFileHandle(dat)
        dat2 = f2.read()
        """
        self.content = content
        self.readpos = 0
    
    def read(self, length = -1):
        out = b""
        if length == -1:
            out = self.content[self.readpos:]
            self.readpos = len(self.content)
        else:
            out = self.content[self.readpos:(self.readpos+length)]
            self.readpos += length
        return out
    
    def tell(self):
        return self.readpos
    
    def seek(self, new_pos):
        self.readpos = new_pos


def encode_special_characters(query):
    return urllib.parse.quote(query) # encode special characters, URL style

def decode_special_characters(query):
    return urllib.parse.unquote(query) # encode special characters, URL style


def remote_png_to_numpy(url):
    """
    @brief: Download a PNG file to RAM and convert to numpy array.
    
    @param  url (str) Remote file location
    @return arr (3d numpy array of int) 
                Image as numpy array.
                Shape is (height, width, channel)
    """
    print("Downloading", url)
    img_request = requests.get(url)
    filehandle  = FakeFileHandle( content = img_request.content )
    pil_image   = PngImagePlugin.PngImageFile(filehandle).convert("RGB")
    arr         = np.array(pil_image, dtype=int)
    return arr

def remote_json_to_py(url):
    """
    @brief: Downlad a JSON file to RAM and convert it to a python data type.
    
    @param  url (str) Remote file location
    @return p (list or dict)
    """
    print("Downloading", url)
    json_request = requests.get(url)
    print("response=", json_request.content.decode("utf-8"))
    p = json.JSONDecoder().decode( s = json_request.content.decode("utf-8") )
    return p
    
