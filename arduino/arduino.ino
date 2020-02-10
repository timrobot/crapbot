/*
        Arduino Brushless Motor Control
     by Dejan, https://howtomechatronics.com
*/
#include <Servo.h>
Servo ESC;     // create servo object to control the ESC
int potValue;  // value from the analog pin
void setup() {
  // Attach the ESC on pin 9
  ESC.attach(9,10000,20000); // (pin, min pulse width, max pulse width in microseconds) 
}
void loop() {
  //potValue = 512;
  //potValue = map(potValue, 0, 1023, 0, 180);   // scale it to use it with the servo library (value between 0 and 180)
  ESC.write(135);    // Send the signal to the ESC
}
