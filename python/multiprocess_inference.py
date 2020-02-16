#!/usr/bin/env python3
import subprocess
import time
import signal
import os
import pyshm
import rccomms
import cam
import policy
import numpy as np

done = False
def stopme(sig, _):
  done = True
signal.signal(signal.SIGTERM, stopme)

# create pipeline to the ps4 gamepad
pyshm.create_shm()
child_proc = subprocess.Popen("sudo python2 ps4gamepad_interface.py".split())

# attach the camera and arduino
cam = FastCam()
arduino = rccomms.RCComms()

# run our camera grabber, ps4 grabber and arduino controller
agent = policy.FastCamPolicy()
while not done:
  cam.update()
  steer, speed, autonomous = pyshm.vals()
  if autonomous:
    action = agent(cam.color)
    steer = np.clip(int((action[0] + 1.0) * 45.0), 0, 90)
    speed = np.clip(int((action[1] + 1.0) * 45.0), 0, 90)
  arduino.write(steer, speed, throttleHz=100.0)

# clean up by closing the arduino, child process and deleting shared memory
# the camera will close by itself
arduino.disconnect()
child_proc.terminate()
pyshm.delete_shm()
time.sleep(1) # wait a little so that the processes can end
