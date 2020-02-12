import pyshm
import time
import sys

if not pyshm.create_shm():
  print("Couldnt create shm, exiting")
  sys.exit(1)

for i in range(100000):
  print(pyshm.vals())
  time.sleep(0.1)

pyshm.delete_shm()
