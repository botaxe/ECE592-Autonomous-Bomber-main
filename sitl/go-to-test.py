
from header import *
from copter import Copter

# parse arguemnts
parser = argparse.ArgumentParser()
parser.add_argument('--gcs_ip', default='127.0.0.1')
parser.add_argument('--gcs_port', default='4444')
parser.add_argument('--connect', default='udp:127.0.0.1:10000')
args = parser.parse_args()

# connect to copter
connection_string = args.connect
copter = Copter(connection_string)
print("CONNECTED")

# set up socket to send data to GCS
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
gcs_ip = args.gcs_ip
gcs_port = int(args.gcs_port)
s.setblocking(0)
s.bind((gcs_ip, gcs_port))

copter.set_ap_mode("GUIDED")

print("Taking off")

takeoff_alt = 25

copter.vehicle.simple_takeoff(takeoff_alt)  # Take off to target altitude

while True:
    try:
        msg = s.recvfrom(10000000)
        data = msg[0]
        gcsCmd = json.loads(data.decode('utf-8'))
        print("Command Received")
        break
    except:
        ''' ignore '''

print(gcsCmd)

copter.set_ap_mode("GUIDED")

targetCoordinate = LocationGlobalRelative(gcsCmd[0], gcsCmd[1], takeoff_alt)
copter.vehicle.simple_goto(targetCoordinate)
print("GOING TO TARGET")
