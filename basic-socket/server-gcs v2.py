import cv2, socket, numpy, pickle, keyboard, pickle

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
# s = socket.socket(socket.SOCK_DGRAM)
# s.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR, 1)


# ip of computer
# ip = "127.0.0.1"
ip = "192.168.1.70"

port = 6666

s.bind((ip, port))

print("Starting")

while True:
    x = s.recvfrom(10000000)
    # if x:
        # print("received something")
    client_ip = x[1][0]
    data = x[0]
    decode_message = pickle.loads(data, encoding='bytes')
    print(decode_message)
    if keyboard.is_pressed('q'):
        break
