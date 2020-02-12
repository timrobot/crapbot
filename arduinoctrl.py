import serial
import glob
import pyshm
import subprocess
import time
import signal

devices = [x for x in filter(lambda t: "ttyACM" in t, glob.glob("/dev/*"))]
arduino_name = devices[0]

done = False

def stopme(_, errno):
  done = True
  
signal.signal(signal.SIGTERM, stopme)

pyshm.create_shm()
child_proc = subprocess.Popen("sudo -H python2 ps4send.py".split())


with serial.Serial(arduino_name, 57600, timeout=10) as ser:
  while not done:
    vals = pyshm.vals()
    ser.write(bytes(str(chr(vals[0]))), 'utf-8'))
    ser.write(bytes(str(chr(vals[1] | 0x80))), 'utf-8'))
    time.sleep(0.001)

child_proc.terminate()

pyshm.delete_shm()
ser.close()

time.sleep(1)
