from header import *

class Copter():

    def __init__(self, connection_string=None, vehicle=None):
        """ Initialize the object
        Use either the provided vehicle object or the connections tring to connect to the autopilot

        Input:
            connection_string       - the mavproxy style connection string, like tcp:127.0.0.1:5760
                                      default is None
            vehicle                 - dronekit vehicle object, coming from another instance (default is None)


        """

        #---- Connecting with the vehicle, using either the provided vehicle or the connection string
        if not vehicle is None:
            self.vehicle    = vehicle
            print("Using the provided vehicle")
        elif not connection_string is None:

            print("Connecting with vehicle...")
            self._connect(connection_string)
        else:
            raise("ERROR: a valid dronekit vehicle or a connection string must be supplied")
            return

        self._setup_listeners()

        self.airspeed           = 0.0       #- [m/s]    airspeed
        self.groundspeed        = 0.0       #- [m/s]    ground speed

        self.pos_lat            = 0.0       #- [deg]    latitude
        self.pos_lon            = 0.0       #- [deg]    longitude
        self.pos_alt_rel        = 0.0       #- [m]      altitude relative to takeoff
        self.pos_alt_abs        = 0.0       #- [m]      above mean sea level

        self.att_roll_deg       = 0.0       #- [deg]    roll
        self.att_pitch_deg      = 0.0       #- [deg]    pitch
        self.att_heading_deg    = 0.0       #- [deg]    magnetic heading

        self.wind_dir_to_deg    = 0.0       #- [deg]    wind direction (where it is going)
        self.wind_dir_from_deg  = 0.0       #- [deg]    wind coming from direction
        self.wind_speed         = 0.0       #- [m/s]    wind speed

        self.climb_rate         = 0.0       #- [m/s]    climb rate
        self.throttle           = 0.0       #- [ ]      throttle (0-100)

        self.ap_mode            = ''        #- []       Autopilot flight mode

        self.mission            = self.vehicle.commands #-- mission items

        self.location_home      = LocationGlobalRelative(0,0,0) #- LocationRelative type home
        self.location_current   = LocationGlobalRelative(0,0,0) #- LocationRelative type current position

        self.FS_SHORT_ACTN = 3

    def _connect(self, connection_string):      #-- (private) Connect to Vehicle
        """ (private) connect with the autopilot

        Input:
            connection_string   - connection string (mavproxy style)
        """
        self.vehicle = connect(connection_string, wait_ready=True, heartbeat_timeout=60)
        self._setup_listeners()

    def _setup_listeners(self):                 #-- (private) Set up listeners
        #----------------------------
        #--- CALLBACKS
        #----------------------------
        if True:
            #---- DEFINE CALLBACKS HERE!!!
            @self.vehicle.on_message('ATTITUDE')
            def listener(vehicle, name, message):          #--- Attitude
                self.att_roll_deg   = math.degrees(message.roll)
                self.att_pitch_deg  = math.degrees(message.pitch)
                self.att_heading_deg = math.degrees(message.yaw)%360

            @self.vehicle.on_message('GLOBAL_POSITION_INT')
            def listener(vehicle, name, message):          #--- Position / Velocity
                self.pos_lat        = message.lat*1e-7
                self.pos_lon        = message.lon*1e-7
                self.pos_alt_rel    = message.relative_alt*1e-3
                self.pos_alt_abs    = message.alt*1e-3
                self.location_current = LocationGlobalRelative(self.pos_lat, self.pos_lon, self.pos_alt_rel)


            @self.vehicle.on_message('VFR_HUD')
            def listener(vehicle, name, message):          #--- HUD
                self.airspeed       = message.airspeed
                self.groundspeed    = message.groundspeed
                self.throttle       = message.throttle
                self.climb_rate     = message.climb

            @self.vehicle.on_message('WIND')
            def listener(vehicle, name, message):          #--- WIND
                self.wind_speed         = message.speed
                self.wind_dir_from_deg  = message.direction % 360
                self.wind_dir_to_deg    = (self.wind_dir_from_deg + 180) % 360


        return (self.vehicle)
        print(">> Connection Established")

    def _get_location_metres(self, original_location, dNorth, dEast, is_global=False):
        """
        Returns a Location object containing the latitude/longitude `dNorth` and `dEast` metres from the
        specified `original_location`. The returned Location has the same `alt and `is_relative` values
        as `original_location`.
        The function is useful when you want to move the vehicle around specifying locations relative to
        the current vehicle position.
        The algorithm is relatively accurate over small distances (10m within 1km) except close to the poles.
        For more information see:
        http://gis.stackexchange.com/questions/2951/algorithm-for-offsetting-a-latitude-longitude-by-some-amount-of-meters
        """
        earth_radius=6378137.0 #Radius of "spherical" earth
        #Coordinate offsets in radians
        dLat = dNorth/earth_radius
        dLon = dEast/(earth_radius*math.cos(math.pi*original_location.lat/180))

        #New position in decimal degrees
        newlat = original_location.lat + (dLat * 180/math.pi)
        newlon = original_location.lon + (dLon * 180/math.pi)

        if is_global:
            return LocationGlobal(newlat, newlon,original_location.alt)
        else:
            return LocationGlobalRelative(newlat, newlon,original_location.alt)

    def is_armed(self):                         #-- Check whether uav is armed
        """
        Checks whether the UAV is armed
        """
        return(self.vehicle.armed)

    def arm(self):                              #-- arm the UAV
        """
        Arm the UAV
        """
        self.vehicle.armed = True

    def disarm(self):                           #-- disarm UAV
        """
        Disarm the UAV
        """
        self.vehicle.armed = False

    def set_airspeed(self, speed):              #--- Set target airspeed
        """
        Set uav airspeed m/s
        """
        self.vehicle.airspeed = speed

    def set_ap_mode(self, mode):                #--- Set Autopilot mode
        """
        Set Autopilot mode
        """
        time_0 = time.time()
        try:
            tgt_mode    = VehicleMode(mode)
        except:
            return(False)

        while (self.get_ap_mode() != tgt_mode):
            self.vehicle.mode  = tgt_mode
            print("Setting mode: %s" % tgt_mode)
            time.sleep(0.2)
            if time.time() < time_0 + 5:
                return (False)

        return (True)

    def get_ap_mode(self):                      #--- Get the autopilot mode
        """
        Get the autopilot mode
        """
        self._ap_mode  = self.vehicle.mode
        return(self.vehicle.mode)

    def clear_mission(self):                    #--- Clear the onboard mission
        """
        Clear the current mission.
        """
        cmds = self.vehicle.commands
        self.vehicle.commands.clear()
        self.vehicle.flush()
        self.vehicle.commands.upload()

    def download_mission(self):                 #--- download the mission
        """ Download the current mission from the vehicle.

        """
        self.vehicle.commands.download()
        self.vehicle.commands.wait_ready() # wait until download is complete.
        self.mission = self.vehicle.commands

    def mission_add_takeoff(self, takeoff_altitude=50, takeoff_pitch=15, heading=None):
        """ Adds a takeoff item to the UAV mission, if it's not defined yet

        Input:
            takeoff_altitude    - [m]   altitude at which the takeoff is considered over
            takeoff_pitch       - [deg] pitch angle during takeoff
            heading             - [deg] heading angle during takeoff (default is the current)
        """
        if heading is None: heading = self.att_heading_deg

        self.download_mission()
        #-- save the mission: copy in the memory
        tmp_mission = list(self.mission)

        print(tmp_mission.count)
        is_mission  = False
        if len(tmp_mission) >= 1:
            is_mission = True
            print("Current mission:")
            for item in tmp_mission:
                print(item)
            #-- If takeoff already in the mission, do not do anything

        if is_mission and tmp_mission[0].command == mavutil.mavlink.MAV_CMD_NAV_TAKEOFF:
            print ("Takeoff already in the mission")
        else:
            print("Takeoff not in the mission: adding")
            self.clear_mission()
            takeoff_item = Command( 0, 0, 0, 3, mavutil.mavlink.MAV_CMD_NAV_TAKEOFF, 0, 0, takeoff_pitch,  0, 0, heading, 0,  0, takeoff_altitude)
            self.mission.add(takeoff_item)
            for item in tmp_mission:
                self.mission.add(item)
            self.vehicle.flush()
            print("Takeoff added to current mission")

    def set_home(self, altitude=50):
        while self.pos_lat == 0.0:
            time.sleep(0.5)
            print ("Waiting for good GPS...")
        self.location_home      = LocationGlobalRelative(self.pos_lat,self.pos_lon,altitude)
        print("Home is saved as %s" % self.location_home)


    def arm_and_takeoff(self, altitude=50, pitch_deg=12):
        """
         Arms the UAV and takeoff
        Planes need a takeoff item in the mission and to be set into AUTO mode. The
        heading is kept constant

        Input:
            altitude    - altitude at which the takeoff is concluded
            pitch_deg   - pitch angle during takeoff
        """
        self.mission_add_takeoff(takeoff_altitude=altitude, takeoff_pitch=pitch_deg)
        print ("Takeoff added to mission")

        while not self.vehicle.armed:
            print("Wait to be armed...")
            time.sleep(1.0)

        print ("Vehicle is Armable: try to arm")
        self.set_ap_mode("MANUAL")

        if not self.vehicle.armed:
            print("NOT ARMED")

        #--- Set to auto and check the ALTITUDE
        if self.vehicle.armed:
            print ("ARMED")
            self.set_ap_mode("AUTO")

            while self.pos_alt_rel <= altitude:
                print ("Altitude = %.0f"%self.pos_alt_rel)
                time.sleep(2.0)

            print("Altitude reached: set to GUIDED")
            self.set_ap_mode("GUIDED")

            time.sleep(1.0)

            print("Sending to the home")
            self.vehicle.simple_goto(self.location_home)

        return True

    def get_target_from_bearing(self, original_location, ang, dist, altitude=None):
        """
        Create a TGT request packet located at a bearing and distance from the original point

        Inputs:
            ang     - [rad] Angle respect to North (clockwise)
            dist    - [m]   Distance from the actual location
            altitude- [m]
        Returns:
            location - Dronekit compatible
        """

        if altitude is None: altitude = original_location.alt

        # print '---------------------- simulate_target_packet'
        dNorth  = dist*math.cos(ang)
        dEast   = dist*math.sin(ang)
        # print "Based on the actual heading of %.0f, the relative target's coordinates are %.1f m North, %.1f m East" % (math.degrees(ang), dNorth, dEast)

        #-- Get the Lat and Lon
        tgt     = self._get_location_metres(original_location, dNorth, dEast)

        tgt.alt = altitude
        # print "Obtained the following target", tgt.lat, tgt.lon, tgt.alt

        return tgt

    def ground_course_2_location(self, angle_deg, altitude=None):
        """
        Creates a target to aim to in order to follow the ground course
        Input:
            angle_deg   - target ground course
            altitude    - target altitude (default the current)

        """
        tgt = self.get_target_from_bearing(original_location=self.location_current,
                                             ang=math.radians(angle_deg),
                                             dist=5000,
                                             altitude=altitude)
        return(tgt)

    def goto(self, location):
        """
        Go to a location

        Input:
            location    - LocationGlobal or LocationGlobalRelative object

        """
        self.vehicle.simple_goto(location)

    def set_ground_course(self, angle_deg, altitude=None):
        """
        Set a ground course

        Input:
            angle_deg   - [deg] target heading
            altitude    - [m]   target altitude (default the current)

        """

        #-- command the angles directly
        self.goto(self.ground_course_2_location(angle_deg, altitude))

    def readmission(self, aFileName):
        print("Reading waypoints from file: %s" % aFileName)
        cmds = self.vehicle.commands
        missionlist=[]
        with open(aFileName) as f:
            for i, line in enumerate(f):
                if i==0:
                    if not line.startswith('QGC WPL 110'):
                        raise Exception('File is not supported WP version')
                else:
                    linearray=line.split('\t')
                    ln_index=int(linearray[0])
                    ln_currentwp=int(linearray[1])
                    ln_frame=int(linearray[2])
                    ln_command=int(linearray[3])
                    ln_param1=float(linearray[4])
                    ln_param2=float(linearray[5])
                    ln_param3=float(linearray[6])
                    ln_param4=float(linearray[7])
                    ln_param5=float(linearray[8])
                    ln_param6=float(linearray[9])
                    ln_param7=float(linearray[10])
                    ln_autocontinue=int(linearray[11].strip())
                    cmd = Command( 0, 0, 0, ln_frame, ln_command, ln_currentwp, ln_autocontinue, ln_param1, ln_param2, ln_param3, ln_param4, ln_param5, ln_param6, ln_param7)
                    missionlist.append(cmd)
        return missionlist

    def get_distance_metres(self, aLocation1):
        """
        Returns the ground distance in metres between two LocationGlobal objects.

        This method is an approximation, and will not be accurate over large distances and close to the
        earth's poles. It comes from the ArduPilot test code:
        https://github.com/diydrones/ardupilot/blob/master/Tools/autotest/common.py
        """
        # print("PLANE : lat=" + str(self.pos_lat) + " lon=" + str(self.pos_lon))
        # print("COMMAND : lat=" + str(aLocation1.lat) + " lon=" + str(aLocation1.lon))
        dlat = aLocation1.lat - self.pos_lat
        dlong = aLocation1.lon - self.pos_lon
        return float(math.sqrt((dlat*dlat) + (dlong*dlong)) * 1.113195e5)

    def distance_to_current_waypoint(self, lat, lon, alt):
        """
        Gets distance in metres to the current waypoint.
        It returns None for the first waypoint (Home location).
        """
        targetWaypointLocation = LocationGlobalRelative(lat,lon,alt)
        distancetopoint = self.get_distance_metres(targetWaypointLocation)
        return distancetopoint
