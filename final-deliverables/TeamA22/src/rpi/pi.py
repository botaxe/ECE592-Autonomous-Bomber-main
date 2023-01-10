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
'''


from header import *
from copter import Copter

# parse arguemnts from command line
parser = argparse.ArgumentParser()
parser.add_argument('--gcs_ip', default='192.168.1.148')
parser.add_argument('--gcs_port', default='4444')
parser.add_argument('--rpi_ip', default='192.168.1.147')
parser.add_argument('--rpi_port', default='5555')
parser.add_argument('--connect', default='udp:127.0.0.1:10000')
args = parser.parse_args()

# connect to copter on localhost
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
res = '480p'
cap = cv2.VideoCapture(0)
out = cv2.VideoWriter(filename, get_video_type(filename), 25, get_dims(cap, res))
color = (40, 147, 200)

# Check if camera opened successfully
if (cap.isOpened()== False):
  print("Error opening camera")

# setup listeners to get all messages from the copter
copter._setup_listeners()

# give some time for all changes to take place
time.sleep(2)

# print current coordinates to check for good GPS signal
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

# print mission items for verification
print("MISSION LIST: \n" + str(missionlist))

# set copter to guided autopilot mode
copter.set_ap_mode("GUIDED")

print("Taking off")

# setting takeoff altitude
takeoff_alt = 25

# take off to target altitude
copter.vehicle.simple_takeoff(takeoff_alt)

# wait while copter reaches desired altitude
while copter.pos_alt_rel < takeoff_alt:
    print("Gaining altitude")
    time.sleep(1)

time.sleep(5)

copter.vehicle.airspeed = 5

# parse through each waypoint in file
for command in missionlist:
    # go to waypoint
    point1 = LocationGlobalRelative(command.x, command.y, command.z)
    copter.vehicle.simple_goto(point1)
    print("GOING TO NEXT WAYPOINT")

    # while the copter is going to desired waypoint...
    while(copter.distance_to_current_waypoint(command.x, command.y, command.z) > float(position_buffer)):
        print('Distance to waypoint: %s' % (str(copter.distance_to_current_waypoint(command.x, command.y, command.z))))
        time.sleep(0.5)

        # look for blue tarp frame-by-frame
        ret, frame = cap.read()
        frame_center_y, frame_center_x, _ = frame.shape

        # perform a blue filter
        blue = frame[..., BLU_IDX] > BLU_VAL
        red= frame[..., RED_IDX] < RED_VAL_MAX
        green = (frame[..., GRN_IDX] > GRN_VAL_MIN) & (frame[..., GRN_IDX] < GRN_VAL_MAX)

        # get all blue objects from filtered frame
        blue_objects = cv2.bitwise_and(blue.astype(np.uint8), red.astype(np.uint8), green.astype(np.uint8))

        # set all blue targets to be white
        blue_objects[blue_objects == 1] = 255
        targets = detection.find_targets_process(blue_objects)

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
                  # display target location on the camera frame
                  cv2.putText(frame, "{}, {}".format((target_x - frame_center_x/2),(-1*(target_y - frame_center_y/2))), \
                              (target_x, target_y), fontFace = cv2.FONT_HERSHEY_DUPLEX, \
                                  fontScale = 2.0, color = (255, 0, 0), thickness = 3)
                  # create a packet with all relavent information for the GCS
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
                  # convert to bytes for socket data transfer
                  packet_bytes = json.dumps(packet).encode('utf-8')
                  # send data to the GCS
                  s.sendto(packet_bytes, (gcs_ip, gcs_port))

                  # place a dot on the frame where the target was found
                  cv2.circle(frame, (target_x, target_y), radius = 5, color = (0, 255, 0), thickness = -1)

              # write to video
              out.write(frame)

              # Press Q on keyboard to  exit
              if cv2.waitKey(25) & 0xFF == ord('q'):
                break

# set socket behavior
s.setblocking(0)

# wait for calculated coordinates from the GCS
while True:
    try:
        msg = s.recvfrom(4096)
        data = msg[0]
        gcsCmd = json.loads(data.decode('utf-8'))
        print("Command Received")
        break
    except:
        '''print("Waiting for GCS")'''

print(gcsCmd)

# create location object from GCS calculated coordinate
targetCoordinate = LocationGlobalRelative(gcsCmd[0], gcsCmd[1], takeoff_alt)
# go to calculated coordinate
copter.vehicle.simple_goto(targetCoordinate)
print("GOING TO TARGET")

# wait while the copter is travelling to the calculated coordinate
while(copter.distance_to_current_waypoint(gcsCmd[0], gcsCmd[1], takeoff_alt) > float(5)):
    time.sleep(1)
    print("Going to waypoint")

# drop bomb
copter.bomb_away()
print("DROPPED BOMB")

# set autopilot mode to RTL
copter.set_ap_mode("RTL")
