# GCS Program VERSION 3
# Used for plotting "Blue Tarp" points sent by the drone.
# And for sending out bombing runs to the drone.

# Created by Kishan Joshi

import socket, keyboard
import matplotlib.pyplot as plt
import json

# Currently UNUSED LIBRARIES
# Kept in code because I do not know if removing causes issues (but it should not).
import sys
import numpy as np
import pickle

# Set up a UDP Communication Protocol
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# MAKE SURE IP ADDRESS AND PORT NUMBER MATCH ON SERVER AND CLIENT
# IP Address is the device running the SERVER
# ip = "192.168.1.70"
rpi_ip = "127.0.0.1"
rpi_port = 5555
ip = "127.0.0.1"
port = 4444

# Binding must occur on the SERVER
s.bind((ip, port))

# Server setup successful
print("Starting")

# Create the "Map" to view data
fig, ax = plt.subplots()

# MUST CHANGE according to the location of the MAP
# Plots an image on the map under any data points.
img = plt.imread(".\TestGPSLocationMap.png")

# Plot Labels
plt.title("GCS")
plt.xlabel("Latitude")
plt.ylabel("Longitude")

# Range of Coordinates of where we fly.
# Both sets MUST BE THE SAME in order to display data / map properly.
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
        # Unsure what msg[1] is, msg[0] is the DATA WE WANT OF THE ENTIRE RECEIVED MESSAGE
        data = msg[0]
        ip_port = msg[1]
        # Using json to decode data. USE THIS EXACT FORMAT WHEN RECEIVING DATA
        decode_message = json.loads(data.decode('utf-8'))
        # ip_port_decoded = json.loads(ip_port.decode('utf-8'))
        print(ip_port)

        # Currently type(decode_message) is a way of checking whether this is the data we want.
        # The type we are looking for is dictionary.
        # If the message is anything else, the message was NOT meant to be sent to the server.
        if type(decode_message) is dict:
            # print(decode_message)

            # ADD THE LONGITUDE AND LATITUDE TO A LIST (for calculations) AND TO PLOT (for display)

            # IMPORTANT
            # IMPORTANT: Needs to be updated to use GSD coordinates. Currently uses the DRONE'S GPS COORDINATES
            # IMPORTANT

            lonXCoords.append(decode_message['current_lon'])
            latYCoords.append(decode_message['current_lat'])
            # Add to plot, "s" argument is the added point's size.
            ax.scatter(decode_message['current_lon'], decode_message['current_lat'], s = 5)

            # IMPORTANT
            # IMPORTANT: Read the above important statement.
            # IMPORTANT

            plt.pause(0.01) #changed
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

    # Get the closet point to click for bombing with 's'
    if keyboard.is_pressed('c'):
        # If click inputs were previously received:
        if clickX and clickY:
            # Arbitrary (Large) distance
            minDistance = 100
            # Set/Store clickX, clickY variables in new set of variables
            compare = float(clickX)**2 + float(clickY)**2
            sendXlon = float(clickX)
            sendYlat = float(clickY)
            # If new point's distance is shorter then current distance, update
            for x, y in zip(lonXCoords, latYCoords):
                if (compare - (x**2 + y**2)) < minDistance:
                    minDistance = compare - (x**2 + y**2)
                    sendXlon = x
                    sendYlat = y

            # BLOCKING Wait for Input Command
            confirmCommand = input(f"You have selected {sendYlat}, {sendXlon} as your bombing location. Confirm bombing? (y/n)")

            # If INPUT for bombing 'y', send a list given [X, Y]
            if confirmCommand == 'y':
                send_data = [sendYlat, sendXlon]
                packet = json.dumps(send_data).encode('utf-8')
                s.sendto(bytes(packet), (rpi_ip, rpi_port)) # pi IP
                print("SENT COORDINATES")

        # Just to check for no clicks, not necessarily needed.
        else:
            print("No Inputs Clicked")

    # Use Input 'a' if you want to find an AVERAGE target location
    # Given a click for a range, where points are found within that range and averaged.
    if keyboard.is_pressed('a'):
        if clickX and clickY:
            sendXlon = float(clickX)
            sendYlat = float(clickY)
            # "NUM/1111111" is a conversion from "Meters / Meters per Degree" to "Degrees".
            # Create a range for points of data to be found in.
            lowerXlimit = sendXlon - (5/111111)
            higherXlimit = sendXlon + (5/111111)
            lowerYlimit = sendYlat - (5 / 111111)
            higherYlimit = sendYlat + (5 / 111111)

            # Make a new "temporary" variables to get the average
            BOMBsetX = 0
            BOMBsetY = 0
            PntsFndinRng = 0
            # Get the range of data points and store the sum and number of points (for averaging)
            for x, y in zip(lonXCoords, latYCoords):
                if lowerXlimit <= x <= higherXlimit:
                    if lowerYlimit <= y <= higherYlimit:
                        PntsFndinRng = PntsFndinRng + 1
                        BOMBsetX = BOMBsetX + x
                        BOMBsetY = BOMBsetY + y
            # Calculate Average Lon and Lat for Bombing
            if PntsFndinRng > 0:
                BOMBsetX = BOMBsetX / PntsFndinRng
                BOMBsetY = BOMBsetY / PntsFndinRng
                confirmCommand = input(
                    f"You have selected {BOMBsetX}, {BOMBsetY} as your bombing location. Confirm bombing? (y/n) ")
                # If INPUT for bombing 'y', send a list given [X, Y]
                if confirmCommand == 'y':
                    send_data = [BOMBsetY, BOMBsetX]
                    packet = json.dumps(send_data).encode('utf-8')
                    s.sendto(bytes(packet), (rpi_ip, rpi_port))
                    print("SEND COORDINATES")
            else:
                print("No Inputs found in Range")

        # Just to check for no clicks, not necessarily needed.
        else:
            print("No Inputs Clicked")

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
