# This is a simple test of the Jetson.GPIO library
# To understand more about this library, read /opt/nvidia/jetson-gpio/doc/README.txt

import sys


import Jetson.GPIO as GPIO
from periphery import PWM
import time

# set GPIO mode to BOARD
GPIO.setmode(GPIO.BOARD)
mode = GPIO.getmode()
print(mode)


# Open PWM channel 0, pin 32
pins = range(0,41)
"""
for pin in pins:
	try:
		pwm = PWM(0, pin)
		print("** Channel 0 pin {} works!".format(pin))
	except:
		print("Pin {} does not work".format(pin))
"""
pwm = PWM(0,2)
pwm = PWM(0,0)

#Channel 0 pin 2

# Set frequency to 1 kHz
pwm.frequency = 2e3
# Set duty cycle to 75%
pwm.duty_cycle = 0.25

pwm.enable()

# Change duty cycle to 50%
pwm.duty_cycle = 0.25

time.sleep(5*60)

pwm.close()
