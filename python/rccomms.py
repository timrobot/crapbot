import serial
import glob
import ctypes
import os

# careful! we do not dynamically find the path, so do not move this file
lib = ctypes.cdll.LoadLibrary("../build/cc/libserial.so")
lib.rccar_connect.restype = ctypes.c_int
lib.rccar_write.argtypes = [ctypes.c_int, ctypes.c_int]

class RCComms:
  def __init__(self):
    self._connected = False
    self._speed = None
    self._steer = None

  def __del__(self):
    self.disconnect()

  def disconnect(self):
    if self._connected:
      lib.rccar_disconnect()
      self._connected = False

  def connect(self):
    if lib.rccar_connect():
      self._connected = True
    else:
      raise Exception("Cannot connect to the arduino")

  def connected(self):
    return self._connected

  def write(self, steer=45, speed=22):
    lib.rccar_write(steer, speed)
    self._steer, self._speed = steer, speed

  def vals(self):
    return self._steer, self._speed
