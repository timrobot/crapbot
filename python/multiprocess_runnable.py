#!/usr/bin/env python3
import subprocess
import time
import signal
import os
import pyshm
import rccomms
import cam

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

# create a place to store the data
if "pics" in os.list_dir(os.getcwd()):
  os.rmdir("pics")
os.mkdir("pics")
_timeidx = 0

# run our camera grabber, ps4 grabber and arduino controller
while not done:
  cam.update()
  steer, speed, _ = pyshm.vals()
  arduino.write(steer, speed, throttleHz=100.0)
  print("Arduino vals:", arduino.vals())

  # store the data
  dataitem_name = os.path.join("pics", "%09d_%03d_%03d_%d.png" % \
      (_timeidx, steer, speed, int(arduino.sendtime * 1e6)) )
  cv2.imwrite(dataitem_name, cam.color)
  _timeidx += 1
  if _timeidx >= 1000000000:
    _timeidx = 0

# clean up by closing the arduino, child process and deleting shared memory
# the camera will close by itself
arduino.disconnect()
child_proc.terminate()
pyshm.delete_shm()
time.sleep(1) # wait a little so that the processes can end
