'''
    ECE 592 - Autonomous Bomber
    Ayush Luthra
    Alex Wheelis
    Kishan Joshi
    Harrison Tseng

    MavProxy:
    mavproxy.exe --master="com3" --out=udp:127.0.0.1:14450 --out=udp:127.0.0.1:14560 --out=udp:127.0.0.1:14570
    com3: UAV connected via USB
    10000: Python app
    20000: QGC
    30000: MissionPlanner

    2	0	3	16	0.00000000	0.00000000	0.00000000	0.00000000	35.72806740	-78.69651680	25.000000	1
    3	0	3	16	0.00000000	0.00000000	0.00000000	0.00000000	35.72804120	-78.69679570	25.000000	1
    4	0	3	16	0.00000000	0.00000000	0.00000000	0.00000000	35.72608150	-78.69678500	25.000000	1
    5	0	3	16	0.00000000	0.00000000	0.00000000	0.00000000	35.72602060	-78.69710680	25.000000	1
    6	0	3	16	0.00000000	0.00000000	0.00000000	0.00000000	35.72803250	-78.69714980	25.000000	1
    7	0	3	16	0.00000000	0.00000000	0.00000000	0.00000000	35.72801510	-78.69752530	25.000000	1
    8	0	3	16	0.00000000	0.00000000	0.00000000	0.00000000	35.72602060	-78.69740720	25.000000	1
    9	0	3	16	0.00000000	0.00000000	0.00000000	0.00000000	35.72600320	-78.69775060	25.000000	1
    10	0	3	16	0.00000000	0.00000000	0.00000000	0.00000000	35.72796290	-78.69786860	25.000000	1

'''


from header import *
from copter import Copter

# parse arguemnts
parser = argparse.ArgumentParser()
parser.add_argument('--gcs_ip', default='192.168.1.148')
parser.add_argument('--gcs_port', default='4444')
parser.add_argument('--rpi_ip', default='192.168.1.147')
parser.add_argument('--rpi_port', default='5555')
# parser.add_argument('--gcs_ip', default='127.0.0.1')
# parser.add_argument('--gcs_port', default='4444')
# parser.add_argument('--rpi_ip', default='127.0.0.1')
# parser.add_argument('--rpi_port', default='5555')
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
rpi_port = int(args.rpi_port)
rpi_ip = args.rpi_ip
s.bind((rpi_ip, int(rpi_port)))


# get video recording functions
filename = 'video.avi'
frames_per_second = 24.0
res = '480p'
cap = cv2.VideoCapture(0)
out = cv2.VideoWriter(filename, get_video_type(filename), 25, get_dims(cap, res))
color = (40, 147, 200)
# Check if camera opened successfully
if (cap.isOpened()== False):
  print("Error opening video  file")

copter._setup_listeners()

time.sleep(2)

print("LAT : " + str(copter.pos_lat))
print("LON : " + str(copter .pos_lon))

# check arming status of the copter
while not copter.is_armed():
    # wait for safety pilot to arm
    print("Waiting to be armed...")
    time.sleep(1)
print("ARMED")

time.sleep(2)
# clear all missions from the copter
copter.clear_mission()

# load recon grid flight plan to copter
missionlist = []
file = "recon.waypoints"
missionlist = copter.readmission(file)

# 5m buffer for gps coordinates
position_buffer = 5

print("MISSION LIST: \n" + str(missionlist))

copter.set_ap_mode("GUIDED")

print("Taking off")

takeoff_alt = 25

copter.vehicle.simple_takeoff(takeoff_alt)  # Take off to target altitude

while copter.pos_alt_rel < takeoff_alt:
    print("Gaining altitude")
    time.sleep(1)

time.sleep(5)

copter.vehicle.airspeed = 5

for command in missionlist:
    # go to waypoint
    # set the default travel speed
    point1 = LocationGlobalRelative(command.x, command.y, command.z)
    copter.vehicle.simple_goto(point1)
    print("GOING TO NEXT WAYPOINT")
#
    while(copter.distance_to_current_waypoint(command.x, command.y, command.z) > float(position_buffer)):
        print('Distance to waypoint: %s' % (str(copter.distance_to_current_waypoint(command.x, command.y, command.z))))
        time.sleep(0.5)
        # look for blue tarp
        # Capture frame-by-frame
        ret, frame = cap.read()
        frame_center_y, frame_center_x, _ = frame.shape

        # perform a blue filter
        blue = frame[..., BLU_IDX] > BLU_VAL
        red= frame[..., RED_IDX] < RED_VAL_MAX
        green = (frame[..., GRN_IDX] > GRN_VAL_MIN) & (frame[..., GRN_IDX] < GRN_VAL_MAX)

        blue_objects = cv2.bitwise_and(blue.astype(np.uint8), red.astype(np.uint8), green.astype(np.uint8))

        blue_objects[blue_objects == 1] = 255
        targets = detection.find_targets_process(blue_objects)
        # print(targets)

        # display the origin
        cv2.putText(frame, "(0,0)", \
                          (int(frame_center_x/2) + 15, int(frame_center_y/2)), fontFace = cv2.FONT_HERSHEY_DUPLEX,\
                              fontScale = 1.0, color = (255, 0, 0), thickness = 3)
        cv2.circle(frame, (int(frame_center_x/2), int(frame_center_y/2)),\
                   radius = 5, color = (0, 0, 255),thickness = -1 )
        if ret == True:

          # Display the resulting frame
          if targets:
              for target_x, target_y in targets:
                  #cv2.circle(frame, (target_x, target_y), radius = 10, color = (0, 0, 255),thickness = -1 )
                  # if you want the coordinates for GCS, USE THESE
                  cv2.putText(frame, "{}, {}".format((target_x - frame_center_x/2),(-1*(target_y - frame_center_y/2))), \
                              (target_x, target_y), fontFace = cv2.FONT_HERSHEY_DUPLEX, \
                                  fontScale = 2.0, color = (255, 0, 0), thickness = 3)
                  packet = {
                    "target_x" : target_x - frame_center_x/2,
                    "target_y" : -1*(target_y - frame_center_y/2),
                    "current_alt" : copter.pos_alt_rel,
                    "current_lat" : copter.pos_lat,
                    "current_lon" : copter.pos_lon,
                    "current_pitch" : copter.att_pitch_deg,
                    "current_roll"  : copter.att_roll_deg,
                    "current_yaw" : copter.att_heading_deg
                  }
                  packet_bytes = json.dumps(packet).encode('utf-8')
                  s.sendto(packet_bytes, (gcs_ip, gcs_port))

                  cv2.circle(frame, (target_x, target_y), radius = 5, color = (0, 255, 0), thickness = -1)

              out.write(frame)
              #cv2.imshow('Frame', frame)
              # Press Q on keyboard to  exit
              if cv2.waitKey(25) & 0xFF == ord('q'):
                break

s.setblocking(0)

while True:
    # targetCoordinate = LocationGlobalRelative(copter.pos_lat, copter.pos_lon, takeoff_alt)
    # copter.vehicle.simple_goto(targetCoordinate)
    try:
        msg = s.recvfrom(4096)
        data = msg[0]
        gcsCmd = json.loads(data.decode('utf-8'))
        print("Command Received")
        break
    except:
        '''print("Waiting for GCS")'''

print(gcsCmd)

targetCoordinate = LocationGlobalRelative(gcsCmd[0], gcsCmd[1], takeoff_alt)
copter.vehicle.simple_goto(targetCoordinate)
print("GOING TO TARGET")

while(copter.distance_to_current_waypoint(gcsCmd[0], gcsCmd[1], takeoff_alt) > float(5)):
    time.sleep(1)
    print("Going to waypoint")

# drop bomb
copter.bomb_away()
print("DROPPED BOMB")

copter.set_ap_mode("RTL")
