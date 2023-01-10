'''
    ECE 592 - Autonomous Bomber
    Ayush Luthra
    Alex Wheelis
    Kishan Joshi
    Harrison Tseng
'''
# import necessary libraries
import socket, keyboard
import matplotlib.pyplot as plt
import json
import sys
import numpy as np
import pickle

# Set up a UDP Communication Protocol
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Set RPI ip address and port
rpi_ip = "172.20.15.100"
rpi_port = 5555
# IP Address is the device running the SERVER
ip = "172.20.7.164"
port = 4444

# bind the server ports
s.bind((ip, port))

# set constants from camera hardware
IMAGE_HEIGHT = 1080
IMAGE_WIDTH = 1920
FOCAL_LENGTH = 0.0165
SENSOR_HEIGHT = .00617
SENSOR_WIDTH = .00455

# Server setup successful
print("Starting")

# Create the "Map" to view data
fig, ax = plt.subplots()

# Plots an image on the map under any data points.
img = plt.imread(".\MAP.png")

# Plot Labels
plt.title("GCS")
plt.xlabel("Latitude")
plt.ylabel("Longitude")

# Range of Coordinates of where we fly.
ax.axis([-78.702385, -78.691902, 35.725121, 35.729265])
ax.imshow(img, extent=(-78.702385, -78.691902, 35.725121, 35.729265))

# Temporarily Initialize Map
for i in range(100):
    plt.pause(0.01)

# Hold Data As Lists for X and Y
lonXCoords = []
latYCoords = []

# Store Click Events in these variables
clickX, clickY = '', ''
ip_port = ''

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

    # pull gps coordinates from the parameters
    drone_lat = drone_lat_long_coor[1]
    drone_lon = drone_lat_long_coor[0]

    east_west_const =  1/(111111*np.cos(38*np.pi/180))
    north_south_const = 1/111111 # deg/meters

    lat_lon_const = 1/111111 # deg/meters


    # pull pitch/roll/yaw from the parameters
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

    # return calculated coordinates
    return [lonO, latO]


# Onclick provided by MatPlotLib
# Returns coordinates of any point on the map clicked (in lon, lat format).
def onclick(event):
    # Must be declared global to be stored properly
    global clickX, clickY
    clickX = event.xdata
    clickY = event.ydata
    #Confirmation of Click:
    print("Click Entered")
    print(clickX, clickY)

# Make/Enable Click Events
fig.canvas.mpl_connect('button_press_event', onclick)

# Receive Message from PI (Drone)
def receive_message():
    # Set RECEIVING end of communication to be nonblocking. ABSOLUTELY NECESSARY.
    s.setblocking(0)

    # Try because if you do not receive a message, you will timeout.
    # Instead of timing out, we can keep retrying for a message.
    try:
        # recvfrom is a UDP command, recv is a TCP command, takes in argument (Buffer Size).
        msg = s.recvfrom(4096)
        data = msg[0]
        ip_port = msg[1]
        # Using json to decode data. USE THIS EXACT FORMAT WHEN RECEIVING DATA
        decode_message = json.loads(data.decode('utf-8'))

        # Currently type(decode_message) is a way of checking whether this is the data we want.
        # The type we are looking for is dictionary.
        # If the message is anything else, the message was NOT meant to be sent to the server.
        if type(decode_message) is dict:
            # add all relavent information into lists and pass into GSD function
            lonlat = [decode_message['current_lon'], decode_message['current_lat']]
            xy = [decode_message['target_x'], decode_message['target_y']]
            azimuth = [decode_message['current_pitch'], decode_message['current_roll'], decode_message['current_yaw']]
            returnGSD = get_lat_long_of_target(xy, lonlat, decode_message['current_alt'], azimuth)
            lonXCoords.append(returnGSD[0])
            latYCoords.append(returnGSD[1])
            # Add to plot, "s" argument is the added point's size.
            ax.scatter(returnGSD[0], returnGSD[1], s = 5)
            plt.pause(0.01)
        else:
            # If the message was not intended for us, print the message type.
            print(type(decode_message))

    # Except and triple quotes MUST BE INCLUDED to maintain nonblocking code.
    except socket.error:
        '''no data yet'''


while True:

    # Receive Message Protocol
    receive_message()

    # Terminate GCS if 'q'
    if keyboard.is_pressed('q'):
        break

    if keyboard.is_pressed('c'):
        # If click inputs were previously received:
        if clickX and clickY:
            sendXlon = float(clickX)
            sendYlat = float(clickY)
            confirmCommand = input(f"You have selected {sendYlat}, {sendXlon} as your bombing location. Confirm bombing? (y/n)")

            # If INPUT for bombing 'y', send a list given [X, Y]
            if confirmCommand == 'y':
                print("SENDING COORDINATES")
                send_data = [sendYlat, sendXlon]
                packet = json.dumps(send_data).encode('utf-8')
                s.sendto(bytes(packet), (rpi_ip, rpi_port)) # pi IP
                print("SENT COORDINATES")

    plt.pause(0.01)

# Extra Command that may be necessary / useful later
# plt.show()

# Extra Notes:
# Please note that heavy amounts of data further slows down the plotting, causing a delay.
# Consider using a time.sleep() or equivalent code on the CLIENT SIDE to help slow down data rates.

# When pressing 'q', 'c', 'a', from "keyboard.ispressed()", BE CAREFUL. PROGRAM IS HEAVILY KEYBOARD SENSITIVE.
# PRESSING OUTSIDE OF PROGRAM / COMMAND LINE WILL RUN THE COMMAND
# IMPORTANT NOTE: This is different from the "input()" command.
# Confirmation for bombing MUST BE DONE IN THROUGH THE COMMAND LINE PROMPT (When prompted.)

# You may have to press 'q', 'c', 'a', MULTIPLE TIMES in order for command to process through.
# This is because of the earlier note (slows down plotting and thus the script entirely).

# Currently sending GPS locations as a list [X,Y] or [longitude, latitude].
# You may want to double check whether X = lon and Y = lat (So I don't send the drone to Australia).
