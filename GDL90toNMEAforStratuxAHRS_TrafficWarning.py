import socket
import json
import binascii
from time import sleep
import struct
import pynmea2
import socket
import time
import math
import androidhelper


#version 1.0
#fixes traffic callouts "oclock" to be correct to aircraft heading instead of rrlative to north


def twos_comp(val, bits):
    """compute the 2's complement of int value val used for latitude and longitude"""
    if (val & (1 << (bits - 1))) != 0: # if sign bit is set e.g., 8bit: 128-255
        val = val - (1 << bits)        # compute negative value
    return val                         # return positive value as is



class Traffic:
    '''Feed strings per GDL90 spec'''
    def __init__ (self, address, altitude, velocity, heading, latitude, longitude, category, counter):
        self.address = address
        self.altitude = (int(altitude,16) * 25) -1000
        self.velocity = int(velocity,16)
        self.heading = (int(heading,16) * 1.4)
        self.latitude = twos_comp(int(latitude,16), 24) / 46603.37080697993
        self.longitude = twos_comp(int(longitude,16), 24) / 46603.37080697993
        self.category = category

        self.new_traffic_counter = 0

        self.relativeVertical = 0
        self.relativeNorth = 0
        self.relativeEast = 0
        self.relativeDistance = 0
        self.alarmLevel = 0

class GPSAlt:
    '''calculate GPS altitude'''
    def __init__ (self, gps_alt):
        self.gps_alt = int(gps_alt,16) * 5
        
class Relative:
    '''calculate relative from ownship, returns distances in meters'''
    def __init__ (self, ownship_lat, ownship_lon, traffic_lat, traffic_lon):
        self.east = (traffic_lon - ownship_lon) * 93000 #meters
        self.north = (traffic_lat - ownship_lat) * 111111 #meters




counter = 0
new_traffic_counter = 0
traffic_alert_counter = 4000
traffic_list = []
traffic_list_action_counter = 250
PFLAA_counter = 0
PFLAU_counter = 0

droid = androidhelper.Android()



#set up socket to receive UDP
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(('', 4000))

#set up socket to send out UDP
#UDP_IP = "192.168.1.11"
UDP_IP = 'localhost' #"192.168.10.15"  #target of XCSOAR
UDP_PORT = 10110
sock_out = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

print("")
print("Script running, open XCSoar")
print("Configure XCSoar device UDP on port 10110 FLARM")
print("")
print("Announcing traffic:")
print("Distance between 1/2 and 5 miles")
print("Altitude withhin 1300 feet")
print("Minimum 5 minutes between announcements")
print("")
print("Targets are colored:")
print("Red within 700 feet")
print("Orange within 1700 feet")
print("All other targets are blue")
print("")
print("Only targets within 25 miles are displayed")




while True:
    #receive UDP and convert to hex
    data, addr = sock.recvfrom(16000)
    data_hex = binascii.hexlify(data).decode()

    #print(data_hex)





    #find and set ownship
    if data_hex[0] == '7'and data_hex[1] =='e' and data_hex[2] == '0' and data_hex[3] == 'a':
        ownship_report = data_hex

        ownship = Traffic(ownship_report[6] + ownship_report[7] + ownship_report[8] + ownship_report[9] + ownship_report[10] + ownship_report[11], #address
                          ownship_report[24] + ownship_report[25] + ownship_report[26], #altitude
                          ownship_report[30] + ownship_report[31] + ownship_report[32], #velocity
                          ownship_report[36] + ownship_report[37], #heading
                          ownship_report[12] + ownship_report[13] + ownship_report[14] + ownship_report[15] + ownship_report[16] + ownship_report[17], #latitude
                          ownship_report[18] + ownship_report[19] + ownship_report[20] + ownship_report[21] + ownship_report[22] + ownship_report[23], #longtitude
                          ownship_report[38] + ownship_report[39], #category
                          counter
                          )
                          
                          
        #print(ownship.latitude , ownship.longitude)
        #print(type(ownship.category))
        #print('baro altitide:',ownship.altitude)
        

    
    #find and set ownship GPS Altitude
    if data_hex[0] == '7'and data_hex[1] =='e' and data_hex[2] == '0' and data_hex[3] == 'b':
        ownship_MSL_report = data_hex

        ownshipGPS = GPSAlt(ownship_MSL_report[4] + ownship_MSL_report[5] + ownship_MSL_report[6] +ownship_MSL_report[7]) #gps altitude

        

        #####AHRS OPTION####
        #if baro alt is 'fff' (101375), then use GPS altitude. Else, use baro altitude for altitude
        #baro alt will always be 'fff' unless the AHRS with baro alt option is installed
        if ownship.altitude != 101375:
            ownshipGPS.gps_alt = ownship.altitude

        #print('GPS or used altitude is', ownshipGPS.gps_alt)
        





    #find and decode traffic from GDL90
    if data_hex[0] == '7'and data_hex[1] =='e' and data_hex[2] == '1' and data_hex[3] == '4':
        traffic_report = data_hex
        #print(data_hex)

        new_traffic = Traffic(traffic_report[6] + traffic_report[7] + traffic_report[8] + traffic_report[9] + traffic_report[10] + traffic_report[11], #address
                              traffic_report[24] + traffic_report[25] + traffic_report[26], #altitude
                              traffic_report[30] + traffic_report[31] + traffic_report[32], #velocity
                              traffic_report[36] + traffic_report[37], #heading
                              traffic_report[12] + traffic_report[13] + traffic_report[14] + traffic_report[15] + traffic_report[16] + traffic_report[17], #latitude
                              traffic_report[18] + traffic_report[19] + traffic_report[20] + traffic_report[21] + traffic_report[22] + traffic_report[23], #longtitude
                              traffic_report[38] + traffic_report[39], #category
                              counter
                              )


        new_traffic.new_traffic_counter = counter

        #print('ownship GPS is', ownshipGPS.gps_alt)

        

        #calculate traffic attributes
        new_traffic.relativeVertical = (new_traffic.altitude - ownshipGPS.gps_alt ) / 3.281 #meters
        new_traffic.relativeNorth = (new_traffic.latitude - ownship.latitude ) * 111111 #meters
        new_traffic.relativeEast = (new_traffic.longitude - ownship.longitude ) * 93000 #meters
        new_traffic.relativeDistance = math.sqrt(((new_traffic.longitude - ownship.longitude)*92662.181)**2 + ((new_traffic.latitude - ownship.latitude)*110567)**2)
        new_traffic.initialBearing = math.degrees(math.atan2(new_traffic.relativeEast,new_traffic.relativeNorth)) 
        new_traffic.relativeBearing = (new_traffic.initialBearing + 360 ) % 360
        new_traffic.relativeBearing_aircraftRef = (new_traffic.relativeBearing - ownship.heading) % 360
        
        if abs(new_traffic.relativeVertical) < 200: #if within 1000 feet vertical
            new_traffic.alarmLevel = 2
        elif abs(new_traffic.relativeVertical) < 500: #if within 2000 feet vertical
            new_traffic.alarmLevel = 1
        else:
            new_traffic.alarmLevel = 0
            
        if new_traffic.category == '01':        #GDL90 - Light(ICAO)<15,500lbs
            new_traffic.category = 8                #NMEA - powered aircraft
        elif new_traffic.category == '02' or new_traffic.category == '03' or new_traffic.category == '04' or new_traffic.category == '05':  #GDL90 - Small (2), Large (3), High Vortex (4), Heavy (5)
            new_traffic.category = 9                #NMEA - jet aircraft
        elif new_traffic.category == '07':      #GDL90 - helicopter
            new_traffic.category = 3                #NMEA - helicopter
        elif new_traffic.category == '09':      #GDL90 - glider/sailplane
            new_traffic.category = 1                #NMEA - glider
        else:
            new_traffic.category = 0
        

        
        #print(new_traffic.address)
        #print('before',traffic_list)

        #add new_traffic to the traffic_list       

        if new_traffic.relativeDistance < 40000: #set to 40km for flying around

            seen = False
        
            for i, item in enumerate(traffic_list):
                if item.address == new_traffic.address:
                    traffic_list[i] = new_traffic
                    seen = True
                    break
            if not seen:
                traffic_list.append(new_traffic)
                

            #print('after ', traffic_list)


            #for x in range(len(traffic_list)):
                #print('adding new traffic target:',traffic_list[x].address)

        new_traffic_counter = 0

    #print(traffic_list_action_counter)

    #if traffic_list[x].counter is less than counter by a significant margin... 1,000, then remove traffic_list[x] object. reset counter.
    if traffic_list_action_counter > 250:
        #print('new_traffic_counter = 100')

        '''#evaluate list of traffic, if data is stale, delete from list'''
        for y in range(len(traffic_list)):
            #print('evaluate removing from list')
            #print(traffic_list[y].address, traffic_list[y].new_traffic_counter, counter)
            
            #evaluate traffic for audio alerting
            if traffic_alert_counter > 4000 and traffic_list[y].relativeDistance < 8000 and traffic_list[y].relativeDistance > 900 and abs(traffic_list[y].relativeVertical) < 400: #between 3/4 miles and 4 miles and within 1300 ft and every 5 mins max (6000 counter)
                droid.ttsSpeak("traffic")
                if traffic_list[y].relativeBearing_aircraftRef < 17: #correct for 'zero oclock' between bearings of 0 and 16
                    droid.ttsSpeak("twelve")
                else:
                    droid.ttsSpeak(str(round(traffic_list[y].relativeBearing_aircraftRef / 30))) #0 to 12 oclock
                droid.ttsSpeak("oclock")
                droid.ttsSpeak(str(round(traffic_list[y].relativeDistance * .00055,1))) #miles
                droid.ttsSpeak("miles")
                droid.ttsSpeak(str(abs(int(round(traffic_list[y].relativeVertical * 3.28,-2))))) #feet
                if traffic_list[y].relativeVertical > 0:
                    droid.ttsSpeak("feet above")
                else:
                    droid.ttsSpeak("feet below")
                
                print('Traffic alert', traffic_list[y].address, 'at', round(traffic_list[y].relativeDistance * .00055,1), 'miles', int(round(traffic_list[y].relativeVertical * 3.28,-2)), 'feet')
                
                traffic_alert_counter = 0

            if (counter-1300) > traffic_list[y].new_traffic_counter:
                #print('REMOVING', traffic_list[y].address, 'FROM TRAFFIC LIST')
                del traffic_list[y]
                break              

            
        traffic_list_action_counter = 0
        

    #output NMEA
    if PFLAA_counter > 10:
        #use PFLAA for heartbeat on NMEA output
        #PFLAU Structure :              RX , TX , GPS , Power , AlarmLevel , RelativeBearing , AlarmType , RelativeVertical , RelativeDistance
        PFLAU = pynmea2.LAU('PF','LAU',('', '',   '',     '',      '',             '',           '',              '',              ''))
        PFLAU_str = str(PFLAU) + '\n'
        PFLAU_b = PFLAU_str.encode('utf-8')

        sock_out.sendto(PFLAU_b, (UDP_IP, UDP_PORT))

        PFLAA_counter = 0


    if PFLAU_counter > 10 and len(traffic_list) > 0:
        for p in range(len(traffic_list)):
            '''print('traffic address:', traffic_list[p].address)
            print('relativeNorth:', traffic_list[p].relativeNorth)
            print('relativeEast:', traffic_list[p].relativeEast)
            print('relativeVertical:',traffic_list[p].relativeVertical)
            print('distance:',new_traffic.relativeDistance)'''

            #Build traffic output in PFLAA sentances
            #PFLAA structure :                AlarmLevel ,                              RelativeNorth ,                      RelativeEast ,                                 RelativeVertical ,                       ID-Type ,              ID ,                Track ,             TurnRate ,                GroundSpeed ,       ClimbRate ,        Type
            PFLAA = pynmea2.LAA('PF','LAA',(str(traffic_list[p].alarmLevel),    str(traffic_list[p].relativeNorth),          str(traffic_list[p].relativeEast),         str(traffic_list[p].relativeVertical),           '', str(traffic_list[p].address), str(traffic_list[p].heading),    '',       str(traffic_list[p].velocity *0.514444 ) ,   '',    str(traffic_list[p].category)))
            PFLAA_str = str(PFLAA) + '\n'
            PFLAA_b = PFLAA_str.encode('utf-8')

            sock_out.sendto(PFLAA_b, (UDP_IP, UDP_PORT))

               

        PFLAU_counter = 0
        
    

    #print(new_traffic_counter)

    #don't run so fast
    sleep(0.01)
    counter = counter + 1
    traffic_list_action_counter = traffic_list_action_counter + 1
    new_traffic_counter = new_traffic_counter + 1
    PFLAA_counter = PFLAA_counter + 1
    PFLAU_counter = PFLAU_counter + 1
    traffic_alert_counter = traffic_alert_counter + 1


