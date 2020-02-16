import time
import pygame
import signal
import pyshm
import sys
import os

done = False
def stopme(sig, _):
  done = True
signal.signal(signal.SIGTERM, stopme)

try:
  pyshm.access_shm()
except Exception as e:
  print(e)
  sys.exit(1)

# Initialize the joysticks.
pygame.init()
pygame.joystick.init()
joystick = pygame.joystick.Joystick(0)
joystick.init()

while not done:
  #
  # EVENT PROCESSING STEP
  #
  # Possible joystick actions: JOYAXISMOTION, JOYBALLMOTION, JOYBUTTONDOWN,
  # JOYBUTTONUP, JOYHATMOTION

  # get all joystick events
  pygame.event.get()
  # L3 (left/right)
  throttle = joystick.get_axis(4)
  isReverse = joystick.get_axis(3)
  # R2
  steering = joystick.get_axis(0)

  # modify the joystick values to be mapped correctly
  pwmSteering = 50
  steering = steering + 1.0
  throttle = throttle + 1.0
  pwmThrottle = 0
  for i in range(101):
    iratio = float(i)/50.0
    if abs(steering-iratio)<0.02:
      pwmSteering = i
    if abs(throttle-iratio)<0.02:
      pwmThrottle = i
  pwmThrottle = pwmThrottle * 0.66
  pwmThrottle = pwmThrottle + 22
  pwmThrottle = int(pwmThrottle)
  pwmSteering = pwmSteering * 0.8
  pwmSteering = pwmSteering + 40
  pwmSteering = 80 - (pwmSteering - 80)
  if(isReverse > 0):
      pwmThrottle = 11

  # send over the values to the shared memory interface
  pyshm.set_vals(pwmSteering, pwmThrottle)
  time.sleep(0.001)

# clean up by closing pygame and deaccessing the shared memory
pygame.quit()
pyshm.deaccess_shm()
