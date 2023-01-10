# import libraries for gcs communication
import socket, pickle, os, keyboard, time, json

#import libraries for object detection
import cv2
from scipy.signal import medfilt
from scipy.signal import find_peaks
import matplotlib.pyplot as plt
import detection
import os

#import libraries for UAV communication
from dronekit import connect, VehicleMode, LocationGlobalRelative, Command, Battery, LocationGlobal, Attitude
from pymavlink import mavutil
import time, math, psutil, copy
import numpy as np

#import misc. libraries
import argparse

from detection import *
