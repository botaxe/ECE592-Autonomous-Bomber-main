import socket, keyboard, time, json

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

ip = "127.0.0.1"
port = 4444

BOMBsetX = 35.727
BOMBsetY = -78.695

while True:
    time.sleep(.1)
    if keyboard.is_pressed('s'):
        send_data = [BOMBsetX, BOMBsetY]
        packet = json.dumps(send_data).encode('utf-8')
        s.sendto(bytes(packet), (ip, port))
        print("Sent data")
