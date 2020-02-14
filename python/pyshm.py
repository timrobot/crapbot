import ctypes
import os
import numpy as np

# careful! we do not dynamically find the path, so do not move this file
lib = ctypes.cdll.LoadLibrary("../cc/build/libpyshm.so")
lib.create_shm.restype = ctypes.c_int
lib.access_shm.restype = ctypes.c_int
lib.val0.restype = ctypes.c_int
lib.val1.restype = ctypes.c_int
lib.set_vals.argtypes = [ctypes.c_int, ctypes.c_int]

def create_shm():
  if not lib.create_shm():
    raise Exception("Could not create shared memory")

def access_shm():
  if not lib.access_shm():
    raise Exception("Could not access shared memory")

def deaccess_shm():
  lib.deaccess_shm()

def delete_shm():
  lib.delete_shm()

def vals():
  return lib.val0(), lib.val1()

def set_vals(a, b):
  lib.set_vals(a, b)
