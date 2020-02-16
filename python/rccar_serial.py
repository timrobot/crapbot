import ctypes
import os
import numpy as np

# careful! we do not dynamically find the path, so do not move this file
lib = ctypes.cdll.LoadLibrary("../build/libserial.so")
lib.rccar_connect.restype = ctypes.c_int
lib.rccar_write.argtypes = [ctypes.c_int, ctypes.c_int]

def connect():
  return lib.rccar_connect()

def write(steer, speed):
  lib.rccar_write(steer, speed)

def disconnect():
  lib.rccar_disconnect()
