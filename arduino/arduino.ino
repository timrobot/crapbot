#include <Servo.h>

Servo steer;     // create servo object to control the ESC
Servo motor;
static int steer_dir;
static int motor_vel;

void setup() {
  steer.attach(9, 10000, 20000);
  steer.write(90);
  motor.attach(11, 10000, 20000); // (pin, min pulse width, max pulse width in microseconds)
  motor.write(44);
  Serial.begin(57600);
}

void loop() {
  if (Serial.available() > 0) {
    char c = Serial.read();
    int val = (int)(c & 0x7F);
    int flg = (int)((c & 0x80) >> 7);
    if (flg == 0) {
      steer_dir = val;
    }
    if (flg == 1) {
      motor_vel = val * 2;
    }
    if (flg == 1) {
      speed_vel = val;
    }*/
    speed_vel = val * 2;
  }
  steer.write(steer_dir);
  motor.write(motor_vel);
}
