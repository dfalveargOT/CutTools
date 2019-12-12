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

import CutTool

## Lectura de archivo .jpg o .tiff
# Process to define the name of the classes
name_class = input("Define the name that the results will be saved : ")
class_total = int(input("Define the number of classes to save : "))
print(" ")
print("Running ... ")
cut = CutTool.CutTool(True, class_total, name=name_class)
cut.run()

print("&&& Finished good luck")


