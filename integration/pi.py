'''
    ECE 592 - Autonomous Bomber
    Ayush Luthra
    Alex Wheelis
    Kishan Joshi
    Harrison Tseng

    MavProxy:
    mavproxy.exe --master="com3" --out=udp:127.0.0.1:14450 --out=udp:127.0.0.1:14560 --out=udp:127.0.0.1:14570
    com3: UAV connected via USB
    14450: Python app
    14560: QGC
    14570: MissionPlanner
'''

from header import *

from copter import Copter

parser = argparse.ArgumentParser()
parser.add_argument('--gcs_ip', default='127.0.0.1')
parser.add_argument('--gcs_port', default='6666')
parser.add_argument('--connect', default='udp:127.0.0.1:14450')
args = parser.parse_args()

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

# set up socket to send data to GCS
send = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
send.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 10000000)
gcs_ip = args.gcs_ip
gcs_port = args.gcs_port

# create plane object and connect
connection_string = args.connect
plane = Plane(connection_string)
print("CONNECTED")
plane.clear_mission()

'''
STAGE 1 : reconnaissance flight
 - Perform grid flight over bounded region
 - Send target data to GCS
 - Loiter when reconnaissance flight is complete
'''

plane._setup_listeners()

time.sleep(2)

print("LAT : " + str(plane.pos_lat))
print("LON : " + str(plane.pos_lon))

while plane.get_ap_mode() != "LOITER":
    time.sleep(1)

# check arming status of the plane
while not plane.is_armed():
    # wait for safety pilot to arm
    print("Waiting to be armed...")
    time.sleep(1)
print("ARMED")

plane.set_ap_mode("GUIDED")

time.sleep(2)
# clear all missions from the plane
plane.clear_mission()


# load recon grid flight plan to plane
missionlist = []
# 0 - x, 1 - y, 2 - z
locations = []

file = "recon.waypoints"
missionlist = plane.readmission(file)

cmds = plane.vehicle.commands
cmds.clear()
cmds.upload()
position_buffer = 5 # 5m buffer for gps coordinates

print("MISSION LIST " + str(missionlist))

for command in missionlist:
    # go to waypoint
    cmds.add(command)
    cmds.upload()
    # while waypoint not reached, detect blue tarp
    # print("LAT : " + str(plane.pos_lat))
    # print("LON : " + str(plane.pos_lon))
    # print("ALT : " + str(plane.pos_alt_rel))

    while(plane.distance_to_current_waypoint(command.x, command.y, command.z) > float(position_buffer)):
        print('Distance to waypoint: %s' % (str(plane.distance_to_current_waypoint(command.x, command.y, command.z))))
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
        print(targets)

        # display the origin
        cv2.putText(frame, "(0,0)", \
                          (int(frame_center_x/2) + 15, int(frame_center_y/2)), fontFace = cv2.FONT_HERSHEY_DUPLEX,\
                              fontScale = 1.0, color = (255, 0, 0), thickness = 3)
        cv2.circle(frame, (int(frame_center_x/2), int(frame_center_y/2)),\
                   radius = 5, color = (0, 0, 255),thickness = -1 )
        if ret == True:

          # Display the resulting frame
          for target_x, target_y in targets:
              #cv2.circle(frame, (target_x, target_y), radius = 10, color = (0, 0, 255),thickness = -1 )
              # if you want the coordinates for GCS, USE THESE
              cv2.putText(frame, "{}, {}".format((target_x - frame_center_x/2),(-1*(target_y - frame_center_y/2))), \
                          (target_x, target_y), fontFace = cv2.FONT_HERSHEY_DUPLEX, \
                              fontScale = 2.0, color = (255, 0, 0), thickness = 3)
              packet = {
                "target_x" : target_x - frame_center_x/2,
                "target_y" : -1*(target_y - frame_center_y/2),
                "current_alt" : plane.pos_alt_abs,
                "current_lat" : plane.pos_lat,
                "current_lon" : plane.pos_lon
              }
              packet_bytes = json.dumps(packet).encode('utf-8')
              send.sendto(packet_bytes, (gcs_ip, int(gcs_port)))

              cv2.circle(frame, (target_x, target_y), radius = 5, color = (0, 255, 0), thickness = -1)

          out.write(frame)
          #cv2.imshow('Frame', frame)
          # Press Q on keyboard to  exit
          if cv2.waitKey(25) & 0xFF == ord('q'):
            break
    # move to next waypoint


'''
STAGE 2 : Bombing run

'''
# wait for command from GCS
