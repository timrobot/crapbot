#include <csignal>
#include <fcntl.h>
#include <cstdio>
#include <unistd.h>
#include <cstring>
#include <cstdlib>
#include "serial.h"

static bool done;
int stopme(int signo) {
  done = true;
  return 1;
}

int main(int argc, char *argv[]) {
  char msg[256];
  memset(msg, 0, 256);
  int i = 40;
  int dir_ = 1;
  int sts = rccar_connect();
  if (sts) {
    while (!done) {
      rccar_write(i, i);
      usleep(10000);
      i += dir_;
      if (i == 40 || i == 120) {
        dir_ *= -1;
      }
    }
  }

  rccar_disconnect();
  usleep(1000000);
  return 0;
}
