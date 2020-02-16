#!/usr/bin/env python3
import subprocess
import time
import signal
import os
import cv2
import pyshm
import rccomms
from cam import FastCam

done = False
def stopme(sig, _):
  done = True
signal.signal(signal.SIGTERM, stopme)

# create pipeline to the ps4 gamepad
pyshm.create_shm()
#child_proc = subprocess.Popen("sudo python2 ps4gamepad_interface.py".split())

# attach the camera and arduino
cam = FastCam()
#arduino = rccomms.RCComms()
#arduino.connect()

# create a place to store the data
if "pics" in os.listdir(os.getcwd()):
  os.system("rm -rf pics")
os.mkdir("pics")
_timeidx = 0

lasttime = time.time()
average_fps = [0.0, 1]

try:
  # run our camera grabber, ps4 grabber and arduino controller
  while not done:
    cam.read()
    steer, speed, _ = pyshm.vals()
    #arduino.write(steer, speed)
    #arduino.write(60, 22)
    #print("Arduino vals:", arduino.vals())

    # store the data
    currtime = time.time()
    dataitem_name = os.path.join("pics", "%09d_%03d_%03d_%d.png" % \
        (_timeidx, steer, speed, int(currtime * 1e6)) )
    cv2.imwrite(dataitem_name, cam.color)
    _timeidx += 1
    if _timeidx >= 1000000000:
      _timeidx = 0
    average_fps = [(currtime - lasttime) / average_fps[1], average_fps[1] + 1]

    #time.sleep(0.005)

finally:
  print("Cleaning up...")
  print(1.0 / average_fps[0])
  # clean up by closing the arduino, child process and deleting shared memory
  # the camera will close by itself
  #arduino.write(80, 22)
  #arduino.disconnect()
  #child_proc.terminate()
  pyshm.delete_shm()
  time.sleep(1) # wait a little so that the processes can end
