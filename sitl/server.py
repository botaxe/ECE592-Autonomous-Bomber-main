# SERVER HAS TO BIND

# CLIENT has to put server IP in args

# SERVER has to put server IP in args

import socket
import sys

if len(sys.argv) == 3:
    # Get "IP address of Server" and also the "port number" from
    #argument 1 and argument 2
    ip = sys.argv[1]
    port = int(sys.argv[2])
else:
    print("Run like : python3 server.py <arg1:server ip:this system IP 192.168.1.6> <arg2:server port:4444 >")
    exit(1)

# Create a UDP socket
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
# Bind the socket to the port
server_address = (ip, port)
s.bind(server_address)
print("Do Ctrl+c to exit the program !!")

while True:
    print("####### Server is listening #######")
    data, address = s.recvfrom(4096)
    print("\n\n 2. Server received: ", data.decode('utf-8'), "\n\n")
    send_data = input("Type some text to send => ")
    s.sendto(send_data.encode('utf-8'), address)
    print("\n\n 1. Server sent : ", send_data,"\n\n")




# from header import *
#
# # parse arguemnts
# parser = argparse.ArgumentParser()
# parser.add_argument('--gcs_ip', default='192.168.184.230')
# parser.add_argument('--gcs_port', default='6666')
# args = parser.parse_args()
#
# # set up socket to send data to GCS
# s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
# r = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
# gcs_ip = "192.168.184.230"
# gcs_port = 6666
# ipPort = (gcs_ip, gcs_port)
# r.bind(ipPort)
#
# packet = {
#   "target_x" : 1,
#   "target_y" : 2,
#   "current_alt" : 3,
#   "current_lat" : 4,
#   "current_lon" : 5
# }
# packet_bytes = json.dumps(packet).encode('utf-8')
#
# s.sendto(packet_bytes, ipPort)
#
# while True:
#     print(receieve_message())
#
#
# # Receive message and upload
# def receive_message():
#     if True:
#         msg = r.recvfrom(10000000)
#         client_ip = msg[1][0]
#         data = msg[0]
#         decode_message = json.loads(data.decode('utf-8'))
#         return decode_message
