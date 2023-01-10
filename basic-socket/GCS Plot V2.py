import cv2, socket, pickle, keyboard, pickle
import numpy as np
import matplotlib.pyplot as plt
import json
import sys


s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
#ip = "192.168.184.230"
ip = "10.152.32.218"

s2 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s2.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 10000000)
ipCLIENT = "10.152.32.218"



port = 4444
s.bind((ip, port))

print("Starting")

img = plt.imread("C:\\Users\\Kishan\\Downloads\\TestGPSLocationv1.png")
plt.title("MAP")
plt.xlabel("Latitude")
plt.ylabel("Longitude")
plt.axis([-78.702385, -78.691902, 35.725121, 35.729265])
plt.imshow(img, extent=(-78.702385, -78.691902, 35.725121, 35.729265))
#plt.axis([100, 700, 100, 700])
#plt.imshow(img, extent=(100, 700, 100, 700))


#Initialize Map
for i in range(100):
    plt.pause(0.01)

# Receive message and upload
def receive_message():
    if True:
        s.setblocking(0)

        try:
            msg = s.recvfrom(10000000)
            client_ip = msg[1][0]
            data = msg[0]
            decode_message = json.loads(data.decode('utf-8'))

            print(decode_message)
            print(type(decode_message))
            if decode_message:
                plt.scatter(decode_message['current_lon'], decode_message['current_lat'], s = 5)
                plt.pause(0.01)
        except socket.error:
            '''no data yet'''
        #print("test")



while True:
    receive_message()
    if keyboard.is_pressed('q'):
        break
    if keyboard.is_pressed('s'):
        send_data = "One"
        s.sendto(send_data.encode('utf-8'), ip)

#plt.show()