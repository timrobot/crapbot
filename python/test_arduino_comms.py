import time
import signal
import rccomms

done = False
def stopme(sig, _):
  done = True
signal.signal(signal.SIGTERM, stopme)

arduino = rccomms.RCComms()
while not done:
  steer, speed = 60, 60
  arduino.write(steer, speed, throttleHz=100.0)

arduino.disconnect()
time.sleep(1)
