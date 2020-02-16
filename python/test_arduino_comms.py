#!/usr/bin/env python3
import time
import signal
import rccomms

done = False
def stopme(sig, _):
  done = True
signal.signal(signal.SIGTERM, stopme)

arduino = rccomms.RCComms()
arduino.connect()
i = 40
dir_ = 1
while not done:
  steer, speed = i, i
  arduino.write(steer, speed)
  time.sleep(0.01)
  i += dir_
  if i == 40 or i == 120:
    dir_ *= -1

arduino.disconnect()
time.sleep(1)
