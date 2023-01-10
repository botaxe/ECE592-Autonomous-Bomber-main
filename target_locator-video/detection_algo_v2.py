#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Feb 28 14:18:01 2022

@author: alex_wheelis


This script takes an image and find targets based off of a certain color 

s
"""

import numpy as np
import cv2

from scipy.signal import medfilt
from scipy.signal import find_peaks
import matplotlib.pyplot as plt


"""

""" 
"""
TASKS:
- identify if the mask over the regular image has the correct color
- identify if the mask is of the correct shape
- given all of this, locate the target


"""

RED_VAL_MAX = 80
RED_VAL_MIN = 0

GRN_VAL_MAX = 160
GRN_VAL_MIN = 130

BLU_VAL = 200

BLU_IDX = 0
GRN_IDX = 1
RED_IDX = 2


object_colors = []

def find_contours(img):
    #image = cv2.imread(img)
    #gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)

    # blurred = cv2.GaussianBlur(gray, (7, 7), 0)
    blurred = cv2.GaussianBlur(img, (9, 9), 0)
    thresh = blurred > 100
    #plt.imshow(thresh)
    #plt.show()
    #print("'find_contours' output: blurred, thresh, image")
    
    return thresh

def split_mask_into_sections(threshold):
    """
    find_contours() will return a ton of hits. All of these need to be parsed.
    create a dictionary of different image slices. These slices will have 
    their colors and shapes confirmed
    """

    # sum of values in col and rows 
    col_sum = np.sum(threshold, axis = 0)
    row_sum = np.sum(threshold, axis = 1)
    
    # get rid of noisy peaks
    col_sum = medfilt(col_sum, kernel_size = 13)
    row_sum = medfilt(row_sum, kernel_size = 13)

    # detect objects
    col_objs, _ = find_peaks(col_sum, height=0)
    row_objs, _ = find_peaks(row_sum, height=0)
        
    # get img snips
    img_snips_dict = {}
    for c in col_objs:
        c = int(c)
        for r in row_objs:
            r = int(r)
            im_snip = threshold[r-10:r+10, c-10:c+10]
            if (im_snip.sum()):
                img_snips_dict[str(c) + "_" + str(r)] = im_snip    
    
    return img_snips_dict

def confirm_color(snippet, mask, color):
    """
    does the shape in the threshold mask have the desired color?
    inputs:
    RGB snippet
    binary mask of object
    (R, G, B) color value
    """
    color_desired = np.array(color)
    color_mean = np.mean(snippet[mask], axis = 0)
    object_colors.append(color_mean)
    print(color_desired)
    print(color_mean)
    
    # look for 30% color distance
    percent = .3
    color_desired_min = color_desired * (1-percent)
    color_desired_max = color_desired * (1+percent)
    
    return ((color_desired_min < color_mean) & (color_mean < color_desired_max)).all()




# execute this to run the target detection script
def find_targets_process(image):

    targets = []
    #print("finding contours")
    #print(image.shape)
    try: 
        middle_col, middle_row = image.shape[0], image.shape[1]
    except: 
        middle_col, middle_row = 0, 0
    
    threshold = find_contours(image)
    #print("contours found")    
    #print("getting snips_dict")
    img_snips_dict = split_mask_into_sections(threshold)
    #print("dict got")
    for key, val in img_snips_dict.items():
        col, row = key.split("_")
        col, row = int(col), int(row)
        '''
        snippet = image[row-10:row+10, col-10:col+10]
        mask = val
        is_target = confirm_color(snippet, mask, color)
        '''
        targets.append([col, row]) 
        #--> you may be able to get rid of the if condition below
    
    return targets
