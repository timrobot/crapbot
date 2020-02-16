#include <Servo.h>

Servo steer;     // create servo object to control the ESC
Servo speed;
static int steer_dir;
static int speed_vel;

void setup() {
  steer.attach(7, 10000, 20000);
  steer.write(90);
  speed.attach(9, 10000, 20000); // (pin, min pulse width, max pulse width in microseconds)
  speed.write(44);
  Serial.begin(57600);
}

void loop() {
  if (Serial.available()) {
    char c = Serial.read();
    int val = (int)(c & 0x7F);
    /*
    int flg = (c & 0x80) >> 7;
    if (flg == 0) {
      steer_dir = val;
    }
    if (flg == 1) {
      speed_vel = val;
    }*/
    speed_vel = val * 2;
  }
  speed.write(speed_vel);
}
