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



# GSD CONVERSION
# img dimensios 720x1280 (heightxwidth)
IMAGE_HEIGHT = 720
IMAGE_WIDTH = 1280

FOCAL_LENGTH = 0.0165 # pulled from https://improvephotography.com/54797/gopro-good-enough-for-an-advanced-photographers/
SENSOR_HEIGHT = .00617
SENSOR_WIDTH = .00455



import numpy as np


def get_lat_long_of_target(target_px_coor, drone_lat_long_coor, drone_alt, drone_azimuth):
    """
    Parameters
    ----------
    target_px_coor : list
        (x, y)
    drone_lat_long_coor : list
        (long, lat)
    drone_alt : int64
        altitude in meters
    drone_azimuth : list
        (pitch, roll, yaw)
        values in radians

    Returns
    -------
    target_lat_long_coor: list

    """

    #Position, decimal degrees
    # PULL GPS COORDINATES
    drone_lat = drone_lat_long_coor[1]
    drone_lon = drone_lat_long_coor[0]

    east_west_const =  1/(111111*np.cos(38*np.pi/180))
    north_south_const = 1/111111# deg/meters <--------------------------- NEED TO FIX THIS

    lat_lon_const = 1/111111# deg/meters <--------------------------- NEED TO FIX THIS


    # PITCH/ROLL CORRECTIONS
    # we need to account for the pitch and roll of the drone
    # the following code will support this

    PITCH = drone_azimuth[0]
    ROLL = drone_azimuth[1]
    YAW = drone_azimuth[2]

    # get offset from angles in meters
    Fy = np.tan(PITCH) * drone_alt
    Fx = np.tan(ROLL) * drone_alt

    # convert Fy and Fx offset to degrees
    Cy = Fy * lat_lon_const
    Cx = Fx * lat_lon_const

    lat = Cy + drone_lat
    lon = Cx + drone_lon

    #-----------------------------------------


    GSD_height = (drone_alt * SENSOR_HEIGHT)/(FOCAL_LENGTH * IMAGE_HEIGHT)
    GSD_width = (drone_alt * SENSOR_WIDTH)/(FOCAL_LENGTH * IMAGE_WIDTH)

    object_x = GSD_width * target_px_coor[0]
    object_y = GSD_height * target_px_coor[1]

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

    #print(latO, lonO, sep = ', ', end="\n")

    return [lonO, latO]


import matplotlib.pyplot as plt
import pandas as pd




def test_gsd(target_px_coor, drone_coor, alt):

    # top left corner of image: 35.727923, -78.698917
    # bottom right corner of image: 35.725613, -78.695241
    lat_long_coors = []

    # test the angles
    for theta in range(-45, 46, 10):
        for phi in range(-45, 46, 10):
            drone_azimuth = [theta, phi, 0]
            lat_long_coors.append(get_lat_long_of_target(target_px_coor, drone_coor, alt, drone_azimuth))


    x = [coor[0] for coor in lat_long_coors]

    y = [coor[1] for coor in lat_long_coors]

    df = pd.DataFrame()
    df["lat"] = y
    df["long"] = x


    fig = plt.subplots(figsize=(8,5))
    plt.title("ANGLES TEST W/ TARGET AT 0,0")
    img = plt.imread("./animal_health_test_img.png")

    plt.imshow(img, extent = [-78.698917,-78.695241, 35.725613, 35.727923])
    plt.scatter(drone_coor[1], drone_coor[0], c = 'r')
    plt.scatter(y, x)
    plt.show()


    lat_long_coors = []
    # test different target locations ex. (0,0) (250, 0)
    for x in range(-5000, 5000, 1000):
        for y in range(-3000, 3000, 500):
            target_px_coor = [y, x]
            lat_long_coors.append(get_lat_long_of_target(target_px_coor, drone_coor, alt, [0,0,0]))


    x = [coor[0] for coor in lat_long_coors]

    y = [coor[1] for coor in lat_long_coors]



    fig = plt.subplots(figsize=(8,5))
    plt.title("TARGET ADJUSTMENT TEST W/ AZIMUTH AT 0, 0, 0")
    img = plt.imread("/Users/alex_wheelis/Desktop/animal_health_test_img.png")

    plt.imshow(img, extent = [-78.698917,-78.695241, 35.725613, 35.727923])
    plt.scatter(drone_coor[1], drone_coor[0], c = 'r')
    plt.scatter(y, x)
    plt.scatter(drone_coor[1], drone_coor[0], c = 'r')

    plt.show()


df = test_gsd((0,0), [35.726471, -78.696820], 25)
