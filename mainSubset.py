#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Oct 28 14:14:18 2019

@author: davidfelipe
"""
"""
PROCESADAS:
    - R3.JPG
    
"""

from CutTool import CutTool
import SubsetCut

## Lectura de archivo .jpg o .tiff
# Process to define the name of the classes

cut = CutTool(False, tool=True)
image, image_name = cut.load_image()

"""
cut procedure
"""
print(" &&& Subsetcut in")
subsetcut = SubsetCut.subsetcut(image, fit=True)
subsetcut.run()
image_segmented = subsetcut.masked_image
print(" &&& Subsetcut out")
print(" ")

print("&&& Finished good luck")


