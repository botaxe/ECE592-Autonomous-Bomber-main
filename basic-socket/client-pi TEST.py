import socket, pickle, os, keyboard, time, json

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 10000000)
ip = "10.152.32.218"




serverport = 4444
while True:
    data = {
        "target_x" : 16,
        "target_y" : 32,
        "current_alt": 40,
        "current_lat": 35.727,
        "current_lon": -78.695
    }
    packet = json.dumps(data).encode('utf-8')
    s.sendto(bytes(packet), (ip, serverport))
    if keyboard.is_pressed('q'):
        break



