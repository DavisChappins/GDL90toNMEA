# GDL90toNMEA
translates GDL90 to NMEA to connect a Stratux to XCSoar


This document describes how to install the necessary components required to use a Stratux or similar ADS-B receiver with XCSoar.

Stratux or similar devices output traffic in the GDL 90 format. XCSoar receives traffic information in the NMEA format. Neither device talks to each other.

This python script decodes GDL 90, manages a traffic list, and outputs that traffic list in NMEA.

Once installed, configured, and running correctly, the normal steps to operate are simply:
Start android phone
Connect android to Stratux wifi network
Open QPython3L, run the script
Open XCSoar


Items required:
Android phone with XCSoar
Stratux or similar GDL 90 ADS-B receiver
QPython 3L installed from Google Play Store
Python script (provided)
Pynmea2 folder (provided)
Working knowledge of XCSoar and adding devices
Working knowledge placing files in your android phone via USB connected to a computer
Working knowledge of a Stratux device (http://192.168.10.1/ when connected to the Stratux wifi)



Steps:
Install QPython 3L through the Google Play store. This allows python to natively run on android.
https://play.google.com/store/apps/details?id=org.qpython.qpy3&hl=en_US&gl=US
[Contribution guidelines for this project](image1.png)

Connect your android phone to a computer via USB and navigate to your phone as a USB drive then qpython\scripts3. Place GDL90toNMEAforStratuxAHRS_TrafficWarning.py here. This is the script that you’ll run.
It should look like this:


With the USB still connected, download the pynmea2 folder and unzip it. Place the entire pynmea2 folder onto your phone at qpython\lib\python3.6\site-packages. This provides the necessary libraries so that python can encode NMEA sentences. If you do not see the QPython folder, you may need to run a script within the QPython 3L application first. On my phone there are two “site-packages” folders with the same name. Not knowing which does what I put the pynmea2 folder in both. You may not have two.
You may have to create the folders called “lib” and “python3.6” and “site-packages”.
It should look like this:



Unplug your android phone from the computer.

Power on the Stratux device

Connect your android phone to the Stratux wifi network

Open a browser and go to 192.168.10.1 the Stratux home page and verify it is receiving 1090 or 978 traffic information and there is a valid GPS fix. The python script cannot pass traffic to XCSoar when it does not have any traffic to pass on.


Open QPython 3L, tap “Programs” then tap “GDL90toNMEAforStratuxAHRS_TrafficWarning” then tap “Run”. QPython3L will run the script and display the python console.




Verify the script is running, QPython 3L will print some messages on the screen notifying you to start XCSoar. This may take up to a minute for it to start running, no idea why. Sometimes it starts up immediately.


Start XCSoar and configure devices (config > devices). Select a device and press EDIT. Choose PORT as UDP Port. Choose TCP Port as 10110. Choose Driver as FLARM. This configures XCSoar to listen to the NMEA output of the python script on UDP port 10110.




If the device says CONNECTED everything is connected properly but there is no traffic data to display. 


If you want, you can see the traffic data in NMEA coming in by pressing MONITOR to see the PFLAU and PFLAA sentences. PFLAU is the heartbeat with PFLAA containing traffic data.



Close devices. Traffic should be displayed on XCSoar’s map page. If you zoom out too far all traffic icons are decluttered.

If you press MONITOR and do not see PFLAU, something has gone wrong:
Check to see that FLARM on UDP port 10110 is a device in XCSoar and is enabled. If it says “No data” instead of “Connected”, check to see if the script is running.
Check QPython 3L to verify the script is still running and has not encountered an error
Check the android wifi settings to verify connection to the Stratux wifi network
Check Stratux at 192.168.10.1 in a browser to verify the Stratux box is operating correctly
There is an error that occurs with the script on startup sometimes, where traffic is detected before own ship altitude. If this occurs click on the x in the top left of the python console then close it, and re-run the script.



Other stuff:
XCSoar has a “FLARM Radar” (config > system > gauges > FLARM, other). Set FLARM radar to OFF. When ON, it displays a radar type view of traffic, this would be useful except its displayed ALL THE TIME when traffic is displayed. I’ve put in a feature request to only display the FLARM radar when traffic targets are within 2km but that has not been addressed (like accepting GDL90).

This python script should work with and without the optional AHRS installed. GPS altitude is used for relatives so that’s always wiggling around and the relative climb of other targets are shown sometimes. With an AHRS it uses baro altitude which is much more steady.

Traffic is displayed at ranges within 25nm. Anything further out is not passed along to XCSoar, even though Stratux may be detecting traffic up to 100nm away.

Since XCSoar does not display relative altitude (only climb rate) on the main map, I’ve used the coloring or warning level to determine relative altitude. Red is within 700 vertical feet of you. Orange is within 1700 vertical feet of you. All others are blue. I put in a feature request to display relative altitude like any other EFB but that also has not been addressed.

The script utilizes android text-to-speech to announce traffic targets within 5 miles of you (but greater than 0.5 miles) and 1100 vertical feet. You may hear something like “Traffic 11 o’clock 3.2 miles 500 feet above”. Why a deadband within 0.5 miles? I have a mode C transponder and ADS-R / TIS-B were providing me with a traffic target (me) at my altitude that kept setting off the alarm. Since I have a mode C and not Mode S I cannot set Stratux to ignore, as the ICAO code is randomly assigned.

The text-to-speech is “dumb” in that once it alerts, it will wait 5 minutes before alerting again. It DOES NOT alert for every traffic object that enters the 5 mile range ring. It’s designed to get you to look at the phone for awareness. Volume can be turned down if it’s annoying.

When you run python on a computer, you can “keyboard interrupt” and stop the script. There is no equivalent for “keyboard interrupt” in QPython 3L. When you run the script it “consumes” port 4000 to listen to GDL 90. If you get an error that says something like “port 4000 is already in use”, that means you have to restart the android device to “un-consume” the port.
