#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Nov  1 19:15:25 2020

@author: foerster
"""
#import PIL
from PIL import PngImagePlugin
import numpy as np
import matplotlib.pyplot as plt

class FakeFileHandle(object):
    def __init__(self, bytestring):
        self.bytestring = bytestring
        self.readpointer = 0
    
    def read(self, length = -1):
        out = b""
        if length == -1:
            out = self.bytestring[self.readpointer:]
            self.readpointer = len(self.bytestring)
        else:
            out = self.bytestring[self.readpointer:(self.readpointer+length)]
            self.readpointer += length
        return out
    
    def tell(self):
        return self.readpointer
    
    def seek(self, new_pos):
        self.readpointer = new_pos

fp = open("87784.png", "rb")
data = fp.read()
fp.close()

fp2 = FakeFileHandle( bytestring = data )

im = PngImagePlugin.PngImageFile(fp2).convert("RGB")

arr = np.array(im)

plt.figure()
plt.imshow(arr)
plt.show()