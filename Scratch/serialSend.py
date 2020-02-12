import serial
import glob

devices = [x for x in filter(lambda t: "ttyACM" in t, glob.glob("/dev/*"))]
#arduino_name = devices[0]

#with serial.Serial(arduino_name, 57600, timeout=10) as ser:
while True:
    led_on = input('Do you want the LED on? ')
    print(led_on)
    #ser.write(bytes(str(chr(ord(led_on) - ord('0'))), 'utf-8'))
