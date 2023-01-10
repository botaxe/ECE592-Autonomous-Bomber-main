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

def CalculateOffset(lat, lon, alt, pitch, roll):
    # Position, decimal degrees
    # PULL GPS COORDINATES
    drone_lat = lat
    drone_lon = lon

    """
    If your displacements aren't too great (less than a few kilometers) 
    and you're not right at the poles, use the quick and dirty estimate 
    that 111,111 meters (111.111 km) in the y direction is 1 degree (of
    latitude) and 111,111 * cos(latitude) meters in the x direction is 
    1 degree (of longitude).
    
    """
    m_to_deg = 1 / 111111  # deg/meters

    # PITCH/ROLL CORRECTIONS
    # we need to account for the pitch and roll of the drone
    # the following code will support this
    DRONE_ALTITUDE = alt  # meters (variable)
    PITCH = pitch  # make sure these are in RADIANS
    ROLL = roll

    # get offset from angles in meters
    Fy = np.tan(PITCH) * DRONE_ALTITUDE
    Fx = np.tan(ROLL) * DRONE_ALTITUDE

    # convert Fy and Fx offset to degrees
    Cy = Fy * m_to_deg
    Cx = Fx * m_to_deg

    lat = Cy + drone_lat
    lon = Cx + drone_lon

    # -----------------------------------------


    # GSD CONVERSION
    # img dimensios 720x1280 (heightxwidth)
    IMAGE_HEIGHT = 720
    IMAGE_WIDTH = 1280

    FOCAL_LENGTH = 0.0165  # pulled from https://improvephotography.com/54797/gopro-good-enough-for-an-advanced-photographers/
    SENSOR_HEIGHT = .00617
    SENSOR_WIDTH = .00455

    GSD_height = (DRONE_ALTITUDE * SENSOR_HEIGHT) / (FOCAL_LENGTH * IMAGE_HEIGHT)
    GSD_width = (DRONE_ALTITUDE * SENSOR_WIDTH) / (FOCAL_LENGTH * IMAGE_WIDTH)

    # to calculate the coordinates of target
    # 1) get px coordinates of target
    # ----> using (-300, 20) as a dummy varible
    # 2) calculate distance away from origin in meters
    # ----> GSD_height * 20
    # ----> GSD_width * -300
    object_coor = (0, 300)
    object_x = GSD_width * object_coor[0]
    object_y = GSD_height * object_coor[1]

    # Earth’s radius, sphere
    R = 6378137

    # offsets in meters
    dn = object_y
    de = object_x

    # Coordinate offsets in radians
    dLat = dn / R
    dLon = de / (R * np.cos(np.pi * lat / 180))

    # OffsetPosition, decimal degrees
    latO = lat + dLat * 180 / np.pi
    lonO = lon + dLon * 180 / np.pi

    print(latO, lonO, sep='\n')
