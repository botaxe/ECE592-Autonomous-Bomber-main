#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Apr  1 11:19:17 2022

@author: alex_wheelis
"""

"""
for GSD of img height
(flight_altitude * sensor_height)
---------------------------------
(focal_length * image_height)

for GSD of img width
(flight_altitude * sensor_width)
---------------------------------
(focal_length * image_width)
"""

import numpy as np

# do all calculations in meters

DRONE_ALTITUDE = 300 # meters (variable)

# img dimensios 720x1280 (heightxwidth)
IMAGE_HEIGHT = 720 
IMAGE_WIDTH = 1280 

FOCAL_LENGTH = 0.0165 # pulled from https://improvephotography.com/54797/gopro-good-enough-for-an-advanced-photographers/
SENSOR_HEIGHT = .00617 
SENSOR_WIDTH = .00455 
 
GSD_height = (DRONE_ALTITUDE * SENSOR_HEIGHT)/(FOCAL_LENGTH * IMAGE_HEIGHT)
GSD_width = (DRONE_ALTITUDE * SENSOR_WIDTH)/(FOCAL_LENGTH * IMAGE_WIDTH)

# to calculate the coordinates of target
# 1) get px coordinates of target
# ----> using (-300, 20) as a dummy varible 
# 2) calculate distance away from origin in meters
# ----> GSD_height * 20
# ----> GSD_width * -300
object_coor = (0, 300)
object_x = GSD_width * object_coor[0]
object_y = GSD_height * object_coor[1]

#Position, decimal degrees
lat = 35.784580
lon = -78.664236

#Earth’s radius, sphere
R=6378137

#offsets in meters
dn = object_y
de = object_x

#Coordinate offsets in radians
dLat = dn/R
dLon = de/(R*np.cos(np.pi*lat/180))

#OffsetPosition, decimal degrees
latO = lat + dLat * 180/np.pi
lonO = lon + dLon * 180/np.pi 

print(latO, lonO, sep = '\n')

