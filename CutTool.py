#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Oct 28 14:13:41 2019

@author: davidfelipe
"""

import cv2 
import numpy as np
import slidingwindow as sw
import yaml
from PyQt5 import QtWidgets
import sys
import os
from osgeo import gdal

class CutTool:
    
    def __init__(self, divide=True, classes=2, path_conf="./", name = "Class", tool=False):
        # Generate the config file
        self.config_file(path_conf)
        # Read the image first
        image, file_name = self.load_image()
        self.image_original = image
        self.raw_image_original = np.copy(image)
        # Flags to control the draw process
        self.activate = False
        self.drawing = False
        self.file_name = file_name[0:(file_name.find("."))]
        # Variables on Drawing process
        self.ref_point = []
        self.class_mode = 1
        self.counter_blocks = 0
        self.blocks = []
        # Generate subsets for big images
        self.generate_subsets(divide, image)
        # Define the Blocks that store the cut process
        self.classes = [] # Array of cuts of the classes
        self.crop_count = np.array([]) # Count of the objects per class
        self.classes_key = []
        self.color_sharp_mode = []
        self.number_count = [] # Store the count for each class after save
        counter = 1
        for i in range (0,classes):
            # Initialization of the variables
            rectangle = []
            color = np.random.choice(range(256), size=3)
            color_c = (int(color[0]), int(color[1]), int(color[2]))
            self.classes.append(rectangle) # initialize the boxes to save the cuts
            self.color_sharp_mode.append(color_c) # assign a different color per Class
            self.crop_count = np.append(self.crop_count,0) ## Initialize the count
            self.classes_key.append(counter)
            self.number_count.append(0)
            counter += 1
            
        # Create the directories to save the information
        if tool == False:
            self.generate_paths(name)
        
    def load_image(self):
        """
        Function load_image
        
        Input :
            None
        
        Process :
            Search certain format files in the directory
            defined in the .yml configured file 
        
        Output :
            image - numpy array 
            image_name - name of the file to be process
        
        """
        self.config_file("./")
        files = os.listdir(self.to_process)
        flag = "None"
        for item in files:
            tiff_flag = item.find(".tif")
            jpg_flag = item.find(".jpg")
            jpeg_flag = item.find(".jpeg")
            png_flag = item.find(".png")
            ovr_flag = item.find(".tif.ovr")
            xml_flag = item.find(".tif.aux.xml")
            if(ovr_flag == -1 and xml_flag == -1 and tiff_flag != -1):
                image_name = item
                flag = "tiff"
                break
            elif(jpg_flag != -1 or jpeg_flag != -1 or png_flag != -1):
                image_name = item
                flag = "default"
                break
        if (flag == "tiff"):
            dataset = gdal.Open(self.to_process + image_name)
            cols = dataset.RasterXSize
            rows = dataset.RasterYSize
            self.transform = dataset.GetGeoTransform()
            data = dataset.ReadAsArray(0, 0, cols, rows)
            image = data.transpose(1,2,0)
            shape = image.shape
            if shape[2] > 3:
                image = np.delete(image,[3],axis=2)
            print(shape)
            shape = image.shape
            print(shape)
            print(" &&& Tiff file found")
            return image.copy(), image_name
        elif (flag == "default"):
            image = cv2.imread(self.to_process + image_name)
            print(" &&& image file found")
            return image, image_name
        else:
            print(" &&& Format file not found in the folder")
            return -1, -1
        
    
    def generate_paths(self, name):
        """
        Function generate_paths
            Create the classes directories to save the information
        Input :
            name : name of the class to save
        Process :
            self.classes_paths = path of the dir for each class
        """
        current_paths = os.listdir(self.results_path)
        self.classes_paths = [] ## List store the save paths of the classes
        for idx in self.classes_key:
            flag = True
            for path in current_paths:
                if path == name + str(idx):
                    flag = False
            if flag:
                os.mkdir(self.results_path + name + str(idx)) # Create the directory on the disk
            self.classes_paths.append(self.results_path + name + str(idx) + "/")
            
        
    def generate_subsets(self, divide, image):
        """
        Function generate_subsets
        Input :
            divide : (true/false) if the image is too big to process
            image : numpy image array to process
        Process :
            self.windows = numpy array's of the original Image
        """
        # Divide Big images in good sizes
        ## Get the screen resolution
        app = QtWidgets.QApplication(sys.argv)
        screen = app.primaryScreen()
        window_available = screen.availableGeometry()
        height = window_available.height()
        min_dimension = height
        if(divide): 
            # Flag that divide the image in screen view parts when it is really big
            self.windows = sw.generate(self.image_original, sw.DimOrder.HeightWidthChannel, min_dimension, self.overlap_subet)
            self.divide = True
        else:
            self.windows = image
            self.divide = False
        
    def mouse_callback(self, event, x, y, flags, param):
        # grab references to the global variables 
        # if the left mouse button was clicked, record the starting 
        # (x, y) coordinates and indicate that cropping is being performed
        if(self.activate):
            if event == cv2.EVENT_LBUTTONDOWN:
                self.ref_point = [(x, y)]
                self.drawing = True
                
            elif event == cv2.EVENT_MOUSEMOVE: 
                if self.drawing==True:
                    a = x 
                    b = y 
                    if a != x | b != y:
                        last = [x+(2*self.line_thickness_def), y+(2*self.line_thickness_def)]
                        crop_part = self.image_raw[self.ref_point[0][1]:last[1], self.ref_point[0][0]:last[0]]
                        self.image[self.ref_point[0][1]:last[1], self.ref_point[0][0]:last[0]] = crop_part
                        cv2.rectangle(self.image, self.ref_point[0], (x,y), (255,0,0), self.line_thickness_draw)
          
            # check to see if the left mouse button was released 
            elif event == cv2.EVENT_LBUTTONUP: 
                self.drawing = False
                # record the ending (x, y) coordinates and indicate that 
                # the cropping operation is finished 
                self.ref_point.append((x, y)) 
                crop_part = self.image_raw[self.ref_point[0][1]:self.ref_point[1][1], self.ref_point[0][0]:self.ref_point[1][0]]
                rectangle = self.classes[self.class_mode - 1]
                rectangle.append((self.ref_point))
                self.crop_count[self.class_mode - 1] += 1
                self.counter_blocks += 1
                # draw a rectangle around the region of interest 
                cv2.rectangle(self.image, self.ref_point[0], self.ref_point[1], self.color_sharp_mode[(self.class_mode-1)], self.line_thickness_draw)
                
    def save_current_window(self, number):
        """
        Function save_current_window
        Input :
            number : number of the subset window to save the information
        """
        ## Run over the rectangles extracted
        for idx, block in enumerate(self.classes):
            counter = 0
            if len(block) > 0:
                ## save the current images on the disk that correspond
                ## to the defined class
                for item in range(self.number_count[idx], len(block)):
                    rect = block[item]
                    name = self.classes_paths[idx] + str(number) + "CutTool"+ self.file_name + "_" + str(counter) + ".jpg"
                    crop_part = self.image_raw[rect[0][1]:rect[1][1], rect[0][0]:rect[1][0]]
                    cv2.imwrite(name, crop_part)
                    counter += 1
                self.number_count[idx] += counter
        print(" Succesfull save of window : " + str(number))
                    

    def config_file(self, path):
        """
        Function config_file
        Input :
            path : path to find the .yaml config file
        """
        
        with open("config.yml", 'r') as ymlfile:
            config_file = yaml.load(ymlfile, Loader=yaml.FullLoader)
        cutTool_conf = config_file['CutTool']
        self.line_thickness_def = cutTool_conf["line_thickness_def"]
        self.line_thickness_draw = cutTool_conf["line_thickness_draw"]
        self.multiplier_erase = cutTool_conf["multiplier_erase"]
        self.overlap_subet = cutTool_conf["overlap"]
        self.results_path = cutTool_conf["results_path"]
        self.to_process = cutTool_conf["to_process"]
        
    def classes_handle(self, key):
        """
        Function classes_handle
            Move over the defined classes
        Input :
            key : number to switch between class_mode
        """
        
        for item in self.classes_key:
            if(key == ord(str(item))):
                self.class_mode = item
                print(" Moved to Draw in class : " + str(item))
                break
    
    def generate_sizes(self, class_mode = 0, verbose = 0):
        rectangle = self.classes[class_mode]
        mean_size = np.array([])
        for item in rectangle:
            h = item[1][1] - item[0][1]
            w = item[1][0] - item[0][0]
            prom = (h+w)/2
            mean_size = np.append(mean_size, prom)
            self.blocks.append((int(prom),int(prom)))
        return mean_size.mean()
            
    def delete_item(self,verbose = 0):
        """
        Function delete_item
            Delete defined boxes in the process
        Input :
            Verbose : Show log messages
        """
        crop_c = self.crop_count[self.class_mode - 1]
        if(crop_c>0):
            rectangle = self.classes[self.class_mode - 1]
            pos = len(rectangle) - 1
            if(len(rectangle)>0):
                limits = rectangle[pos]
                crop_sustitute = self.image_raw[limits[0][1]:(limits[1][1]+self.multiplier_erase*self.line_thickness_def), limits[0][0]:(limits[1][0]+self.multiplier_erase*self.line_thickness_def)]    
                self.image[limits[0][1]:(limits[1][1]+self.multiplier_erase*self.line_thickness_def), limits[0][0]:(limits[1][0]+self.multiplier_erase*self.line_thickness_def)] = crop_sustitute
                del rectangle[pos]
                crop_c -= 1
                self.counter_blocks -= 1
                
        
    def run(self, verbose=0):
        
        cv2.namedWindow("CutTool",cv2.WINDOW_FULLSCREEN) 
        cv2.setMouseCallback("CutTool", self.mouse_callback)
        
        self.counter_windows = 0
        flag = False
        
        for image_subset in self.windows:
            if(self.divide):
                self.image = self.image_original[image_subset.indices()]
            else:
                self.image = self.image_original
            self.image_raw = self.image.copy()
            
            if(self.image.mean() > 225 or self.image.mean() < 20):
                continue
            
            self.counter_windows += 1
            # keep looping until the 'q' key is pressed 
            while True: 
                
                # display the image and wait for a keypress 
                cv2.imshow("CutTool", self.image) 
                key = cv2.waitKey(1) & 0xFF
              
                # press 'r' to reset the window 
                self.classes_handle(key)
                
                if key == ord("o"):
                    flag = True
                    break
                
                elif key == ord("r"): 
                    self.image = self.image_raw.copy()
                    self.ref_point = []
                    
                elif key == ord("a"): 
                    print(self.activate)
                    if(self.activate):
                        self.activate = False
                    else:
                        self.activate = True

                elif key == ord("e"):
                    print("Deleted")
                    self.delete_item()
                    
                elif key == ord("h"):
                    counter = 0
                    for item in self.classes:
                        print("in Class " + str(counter)+ ": " +str(len(item)))
                        counter += 1
                    print("Mode :" + str(self.class_mode))
                    print("Color " + str(self.color_sharp_mode[self.class_mode-1]))
                    print("Window # "+str(self.counter_windows)+" de " + str(len(self.windows)))
                
                    # if the 'c' key is pressed, break from the loop 
                elif key == ord("q"):
                    self.image = self.image_raw.copy()
                    break
                
            ## End of While
            # Generate the sizes and save on the disk
            if flag:
                break
            self.save_current_window(self.counter_windows)
            
        cv2.destroyAllWindows()