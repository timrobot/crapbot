import time
import pygame
import signal
import pyshm

pygame.init()

done = False

def stopme(_, errno):
  done = True
  
signal.signal(signal.SIGTERM, stopme)

# Initialize the joysticks.
pygame.joystick.init()

pyshm.access_shm()

while not done:
        #
    # EVENT PROCESSING STEP
    #
    # Possible joystick actions: JOYAXISMOTION, JOYBALLMOTION, JOYBUTTONDOWN,
    # JOYBUTTONUP, JOYHATMOTION
    for event in pygame.event.get(): # User did something.
        if event.type == pygame.JOYBUTTONDOWN:
            print("Joystick button pressed.")
        elif event.type == pygame.JOYBUTTONUP:
            print("Joystick button released.")
    
    joystick = pygame.joystick.Joystick(0)
    joystick.init()
    #L3(Left/right)
    steering = joystick.get_axis(0)
    pwmSteering = 50
    steering = steering + 1.0
    #R2
    throttle = joystick.get_axis(4)
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
    isReverse = joystick.get_axis(3)
    if(isReverse > 0):
        pwmThrottle = 11
    print("Steering: " + str(pwmSteering) + " Throttle: " + str(pwmThrottle))
    pyshm.set_vals(pwmSteering, pwmThrottle)
    time.sleep(0.001)

pyshm.deaccess_shm()
pygame.quit()
