import socket, keyboard, json

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

ip = "127.0.0.1"
port = 4444

# Binding must occur on the SERVER
s.bind((ip, port))

while True:
    msg = s.recvfrom(10000000)
    # Unsure what msg[1] is, msg[0] is the DATA WE WANT OF THE ENTIRE RECEIVED MESSAGE
    data = msg[0]
    # Using json to decode data. USE THIS EXACT FORMAT WHEN RECEIVING DATA
    decode_message = json.loads(data.decode('utf-8'))
    print("LAT = " + str(decode_message[0]))
    print("LON = " + str(decode_message[1]))
