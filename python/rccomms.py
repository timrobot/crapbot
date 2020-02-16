import serial
import time
import glob
import rccar_serial

class RCComms:
  def __init__(self):
    self._connected = False
    self.sendtime = None
    self._speed = None
    self._steer = None

  def __del__(self):
    self.disconnect()

  def disconnect(self):
    if self._connected:
      rccar_serial.disconnect()
      self._connected = False

  def connect(self):
    if rccar_serial.connect():
      self._connected = True
    else:
      raise Exception("Cannot connect to the arduino")

  def connected(self):
    return self._connected

  def write(self, steer=45, speed=22):
    rccar_serial.write(steer, speed)
    self._steer, self._speed = steer, speed

  def vals(self):
    return self._steer, self._speed
