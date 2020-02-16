#include "serial.h"
#include <csignal>
#include <fcntl.h>
#include <cstdio>
#include <unistd.h>
#include <cstring>
#include <cstdlib>

static bool done;
int stopme(int signo) {
  done = true;
  return 1;
}

int main(int argc, char *argv[]) {
  char msg[256];
  memset(msg, 0, 256);
  serial_t arduino;
  serial_connect(&arduino, "/dev/ttyACM0", 57600);
  int i = 40;
  int dir_ = 1;
  if (arduino.fd != -1) {
    while (!done) {
      msg[0] = i;
      msg[1] = i | 0x80;
      if (write(arduino.fd, msg, strlen(msg)) != -1) {
      }
      usleep(10000);
      i += dir_;
      if (i == 40 || i == 120) {
        dir_ *= -1;
      }
    }
  }

  serial_disconnect(&arduino);
  usleep(1000000);
  return 0;
}
