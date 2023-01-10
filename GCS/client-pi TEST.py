import socket, pickle, os, keyboard, time, json, time

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 10000000)

# SET IP TO THE SERVER'S IP ADDRESS
ip = "127.0.0.1"

# PORTS MUST MATCH BETWEEN SERVER AND IP
serverport = 4444


while True:
    # Change Frequency of sent data
    time.sleep(.1)

    # Sample type "dict" packet format
    # Subject to change after pitch, roll, yaw, etc.
    data = {
        "target_x" : 16,
        "target_y" : 32,
        "current_alt": 40,
        "current_lat": 35.727,
        "current_lon": -78.695
    }
    if keyboard.is_pressed('s'):
        print("Sending data")
        packet = json.dumps(data).encode('utf-8')
        s.sendto(bytes(packet), (ip, serverport))
    if keyboard.is_pressed('q'):
        break
