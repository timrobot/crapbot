import pyshm
import time
import sys

if not pyshm.access_shm():
  print("Couldnt access shm, exiting")
  sys.exit(1)

for i in range(1000):
  pyshm.set_vals(i, i)
  time.sleep(0.2)

pyshm.deaccess_shm()
