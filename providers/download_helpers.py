#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Helper routines for server communication
"""
from PIL import PngImagePlugin
import numpy as np
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
        f    = open("foo.txt", "r") # or "rb"
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


def remote_png_to_numpy(url):
    """
    @brief: Download a PNG file to RAM and convert to numpy array.
    
    @param  url (str) Remote file location
    @return arr (3d numpy array of int) 
                Image as numpy array.
                Shape is (height, width, channel)
    """
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
    json_request = requests.get(url)
    p = json.JSONDecoder().decode( s = json_request.content.decode("utf-8") )
    return p
    