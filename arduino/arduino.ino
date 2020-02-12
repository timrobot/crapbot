/*
        Arduino Brushless Motor Control
     by Dejan, https://howtomechatronics.com
*/
#include <Servo.h>
Servo drive;     // create servo object to control the ESC
static int drive_vel;
Servo wheel;
static int wheel_dir;
void setup() {
  Serial.begin(57600);
  // Attach the ESC on pin 9
  drive.attach(9,10000, 20000); // (pin, min pulse width, max pulse width in microseconds)
  drive.write(45);
  wheel.attach(7,10000, 20000);
  wheel.write(90);
}

void loop() {
  if (Serial.available()) {
    char c = Serial.read();
    int vel = (int)c & 0x7F;
    int id = ((int)c & 0x8) >> 7;
    if (vel < 0) {
      vel = 0;
    }
    if (vel > 90) {
      vel = 90;
    }
    vel *= 2;
    if (id == 0) {
      drive_vel = vel;
      drive.write(drive_vel);
    }
    if (id == 1) {
      wheel_dir = vel;
      wheel.write(wheel_dir);
    }
  }
}
