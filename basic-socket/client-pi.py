import socket, pickle, os, keyboard, time

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 10000000)
# ip = "192.168.1.70"
ip = "127.0.0.1"
serverport = 6666
while True:
    data = b'Test'
    s.sendto(data, (ip, serverport))
    if keyboard.is_pressed('q'):
        break
