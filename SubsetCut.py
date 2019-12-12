#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Aug  1 20:42:31 2019

@author: DavidFelipe
"""

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Jul 13 17:14:59 2019
@author: DavidFelipe
"""

import cv2 
import numpy as np
import yaml
import sys
from PyQt5 import QtWidgets

class subsetcut:
    def __init__(self, image, fit=False, path_conf="./"):
        ## Get the screen resolution
        app = QtWidgets.QApplication(sys.argv)
        screen = app.primaryScreen()
        window_available = screen.availableGeometry()
        width = window_available.width()
        height = window_available.height()
        min_dimension = height
        self.ratio = 1
        ## Image definition to process
        if fit:
            self.image_original = self.image_resize(image, height=min_dimension)
            self.raw_image_original = np.copy(image)
        else:
            self.image_original = image
            self.raw_image_original = np.copy(image)
        self.big_image = image
        ## Control Variables
        self.activate = False
        self.drawing = False
        self.config_file(path_conf)
        self.polygon_done = False
        self.activate_points_del = False # Control Variable activate the erase point option
        ## Objects track
        self.blocks = []
        self.flag_block_points = [] ## Store if the polygon is done
        self.points_clicked = 0
        self.current_point = 0
        self.points = np.array([(0,0)], np.int32)
        self.last = []
        self.current_big = []
        self.ref_point = []
        ## FINAL information
        self.big_points = []
        self.blocks = []
        ## Identifier of procees quantify
        self.pross_num = 0
        ### Graph parameters
        self.radius = 4
        self.color_circle = (0, 0, 255)
        self.color = (0, 255, 0)
        self.color_text = (255,0,0)
        self.height = 0.9
        self.fill_lett = 1
        self.font = cv2.FONT_HERSHEY_SIMPLEX
        ## Fit image
        
    def draw_options(self, key):
        if key == ord("+"):
            self.radius += 1
        elif key == ord("-") and self.radius > 1:
            self.radius -= 1
        
    def poly_area(self, corners):
        n = len(corners) # of corners
        area = 0.0
        for i in range(n):
            j = (i + 1) % n
            area += corners[i][0] * corners[j][1]
            area -= corners[j][0] * corners[i][1]
        area = abs(area) / 2.0
        return area/self.ratio
        
    def extract_subsets(self):
        """
        self.blocks contain the point's boxes
        si divido las coordenadas por el ratio obtengo la
        coordenada real del punto
        """
        x,y,z = self.big_image.shape
        mask_image = np.zeros((x,y))
        
        for block in self.blocks:
            pts = np.array([0,0])
            for point in block:
                point = [point[0]/self.ratio, point[1]/self.ratio]
                pts = np.vstack((pts, point))
            pts = np.delete(pts, [0], axis = 0)
            cv2.fillPoly(mask_image,np.int32([pts]),1,255)
        self.masked_image = cv2.bitwise_and(self.big_image, self.big_image, mask=mask_image.astype(np.uint8)) 
        print("image_masked")
    
    def image_resize(self, image, width = None, height = None, inter = cv2.INTER_AREA):
        # initialize the dimensions of the image to be resized and
        # grab the image size
        dim = None
        (h, w) = image.shape[:2]
    
        # if both the width and height are None, then return the
        # original image
        if width is None and height is None:
            return image
        # check to see if the width is None
        if width is None:
            # calculate the ratio of the height and construct the
            # dimensions
            r = height / float(h)
            dim = (int(w * r), height)
        # otherwise, the height is None
        else:
            # calculate the ratio of the width and construct the
            # dimensions
            r = width / float(w)
            dim = (width, int(h * r))
        # resize the image
        resized = cv2.resize(image, dim, interpolation = inter)
        self.ratio = r
        # return the resized image
        return resized
        
    def show_results(self):
        print("Subset parts extracted : " + str(len(self.blocks)))
        print("Blocks of points : " + str(len(self.big_points)))
        print("Process done " + str(self.pross_num))
        
    def clear_part(self, def_points):
        if len(def_points) > 1:
            pt1 = def_points[0]
            pt2 = def_points[1]
            minx = min(pt1[0], pt2[0]) - 1*self.line_thickness_def
            maxx = max(pt1[0], pt2[0]) + 1*self.line_thickness_def
            miny = min(pt1[1], pt2[1]) - 1*self.line_thickness_def
            maxy = max(pt1[1], pt2[1]) + 1*self.line_thickness_def
            crop_part = self.image_raw[miny:maxy, minx:maxx]
            self.image[miny:maxy, minx:maxx] = crop_part

    def draw_process(self):
        ## Drawing points on the image
        if len(self.big_points)>0:
#            self.image = self.image_raw.copy()
            for idx, block_points in enumerate(self.big_points):
                if self.flag_block_points[idx]:
                    ## Complete box to draw the lines]
                    lenght_total = len(block_points)
                    lines = []
                    # Create the lines for draw the polygon
                    for idx in range(0,lenght_total):
                        if idx != lenght_total - 1:
                            line = [block_points[idx],block_points[idx+1]]
                        else :
                            line = [block_points[idx],block_points[0]]
                        lines.append(line)

                    #area = self.poly_area(block_points)
                    # Draw lines between points
                    for line_item in lines:
                        cv2.line(self.image, line_item[0], line_item[1], self.color, self.line_thickness_draw)

                for point in block_points:
                    cv2.circle(self.image, point, self.radius, self.color_circle, thickness=-1)
                    
    def mouse_callback(self, event, x, y, flags, param):
        # grab references to the global variables 
        # if the left mouse button was clicked, record the starting 
        # (x, y) coordinates and indicate that cropping is being performed
        if(self.activate):
#            try:
            if event == cv2.EVENT_LBUTTONUP:
                self.ref_point = [(x, y)]
                self.points = np.vstack((self.points, (x,y)))
                self.drawing = True
                
                if self.current_point != self.points_clicked:
                    self.image = self.image_raw.copy()
                    self.big_points[self.pross_num].append((x,y))
                    self.points_clicked += 1
                    
                if self.points_clicked == 0:
#                    print("New")
                    self.flag_block_points.append(False)
                    self.current_big = [(x,y)]
                    self.big_points.append(self.current_big)
                    self.points = np.delete(self.points, [0], axis = 0)
                    self.points_clicked += 1
                    
            elif event == cv2.EVENT_MOUSEMOVE: 
                if self.drawing==True:
                    a = x 
                    b = y 
                    if a != x | b != y:
                        self.clear_part(self.last)
                        init = (self.ref_point[0][0], self.ref_point[0][1])
                        cv2.line(self.image, init, (x,y), self.color, self.line_thickness_draw)
                        self.last = [init, (x,y)]
                        
            if self.polygon_done:
                self.polygon_done = False # Flag that handle new polygons
                self.points_clicked = 0
                self.current_point = 0
                self.drawing = False
                self.flag_block_points[self.pross_num] = True
                self.blocks.append(self.points)
                self.points = np.array([0,0], np.int32)
                init = (self.ref_point[0][0], self.ref_point[0][1])
                cv2.line(self.image, init, (x,y), self.color, self.line_thickness_draw)
                self.last = []
                self.pross_num += 1
                self.show_results()
                

    def config_file(self, path):
        with open("config.yml", 'r') as ymlfile:
            config_file = yaml.load(ymlfile, Loader=yaml.FullLoader)
        guicut_conf = config_file['CutTool'] # guicut
        self.line_thickness_def = guicut_conf["line_thickness_def"]
        self.line_thickness_draw = guicut_conf["line_thickness_draw"]
        self.multiplier_erase = guicut_conf["multiplier_erase"]
        self.results_path = guicut_conf["results_path"]
        self.to_process = guicut_conf["to_process"]
        
            
    def delete_item(self,verbose = 0):
        if self.drawing and self.activate_points_del:
            if self.points_clicked != 1:
                last_point = self.points[self.points_clicked-2]
                self.ref_point = [(last_point[0], last_point[1])]
                self.points = np.delete(self.points, [self.points_clicked-1], axis=0)
                self.points_clicked -= 1
                long = len(self.big_points[self.pross_num])
                del self.big_points[self.pross_num][(long - 1)]
                
            elif self.points_clicked == 1:
                self.ref_point = []
                self.points = np.array([0,0], np.int32)
                long = len(self.big_points)
                del self.big_points[long-1]
            self.drawing = True   
        elif self.drawing == False and len(self.big_points)>=1:
            print("Del Big Blocks")
            long = len(self.blocks)
            del self.blocks[long-1]
            long = len(self.big_points)
            del self.big_points[long-1]
            del self.flag_block_points[long-1]
            self.last = []
            self.points_clicked = 0
            self.current_point = 0
            self.pross_num -= 1
        self.image = self.image_raw.copy()
                     
    
    def run(self, verbose=0):
        cv2.namedWindow("image") 
        cv2.setMouseCallback("image", self.mouse_callback)

        self.image = self.image_original
        self.image_raw = self.image.copy()
        print("Ready ... ")
        # keep looping until the 'q' key is pressed 
        while True: 
            
            # display the image and wait for a keypress
            self.draw_process()
            cv2.imshow("image", self.image) 
            key = cv2.waitKey(1) & 0xFF

            self.draw_options(key)
            
            # press 'r' to reset the window 
            if key == ord("r"): 
                self.image = self.image_raw.copy()
                self.points_clicked = 0
                self.ref_point = []
            
            elif key == ord("n"):
                ## new polygon
                print("New Polygon")
                self.polygon_done = True
            
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
                print("\nPoints : " + str(self.points))
                print("Points Clicked : " + str(self.points_clicked))
                print("Flag : " + str(len(self.flag_block_points)))
                print("Len Blocks : " + str(len(self.blocks)) + "\n")
                print("Blocks : ")
                print(self.blocks)
                print("\nBigPoints : ")
                print((self.big_points))
                print("Process num : " + str(self.pross_num))
                print("Polygon Done : " + str(self.polygon_done) + "\n")
                            
            elif key == ord("q"):
                self.draw = False
                
            elif key == 27:
                self.image = self.image_raw.copy()
                ## Exit of the pr225ogram
                break
        if self.pross_num == 0:
            self.masked_image = self.big_image
        else:
            self.extract_subsets() 
            cv2.imwrite("MaskedImage.png", self.masked_image) 
            
            
        del self.image_raw
        cv2.destroyAllWindows()
        