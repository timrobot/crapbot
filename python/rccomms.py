import serial
import time
import glob

class RCComms:
  def __init__(self):
    self.ser = None
    self.sendtime = None
    self._speed = None
    self._steer = None

  def __del__(self):
    self.disconnect()

  def disconnect(self):
    if self.ser is not None:
      self.ser.close()
      self.ser = None

  def connect(self):
    # go through all possible devices in order to connect to the RC Car
    devices = [x for x in filter(lambda t: "ttyACM" in t, glob.glob("/dev/*"))]
    for dname in devices:
      try:
        self.ser = serial.Serial(dname, 57600, timeout=10)
        break
      except Exception as e:
        self.ser = None
    if self.ser is None:
      raise Exception("Cannot connect to the arduino")

  def connected(self):
    return self.ser is not None

  def write(self, steer=45, speed=22, throttleHz=100.0):
    self.ser.write(bytes(str(chr(steer)) + str(chr(speed | 0x80)), "utf-8"))
    """
    end_time = time.time()
    # only send if outside the throttle range
    if self.sendtime is None or \
        ((end_time - self.sendtime) > (1.0 / throttleHz)):
      self.sendtime = end_time
      self._steer, self._speed = steer, speed
    """

  def vals(self):
    return self._steer, self._speed
