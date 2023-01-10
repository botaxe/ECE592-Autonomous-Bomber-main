import cv2, socket, numpy, pickle

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# ip of computer
ip = "192.168.158.192"

port = 6666

s.bind((ip, port))

print("Starting")

while True:
    x = s.recvfrom(10000000)
    if x:
        print("received something")
    client_ip = x[1][0]
    data = x[0]
    print(type(data))
    data = pickle.loads(data, encoding='bytes')

    data = cv2.imdecode(data, cv2.IMREAD_COLOR)
    cv2.imshow('server', data)
    if cv2.waitKey(1) == ord('q'):
        break

cv2.destroyAllWindows()
