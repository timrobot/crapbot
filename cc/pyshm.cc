#include "pyshm.h"
#include <sys/types.h>
#include <sys/ipc.h>
#include <sys/shm.h>
#include <unistd.h>

static int shmvalid;
static int shmid;
static int *values;

int create_shm() {
  shmvalid = 1;
  if ((shmid = shmget(9000, sizeof(2 * sizeof(int)), 0666 | IPC_CREAT)) == -1) {
    struct shmid_ds sds;
    shmctl(shmid, IPC_RMID, &sds);
    if ((shmid = shmget(9000, sizeof(2 * sizeof(int)), 0666 | IPC_CREAT)) == -1) {
      return 0;
    }
  }

  if ((values = (int *)shmat(shmid, nullptr, 0666)) == (int *) -1) {
    shmvalid = 0;
  }

  return shmvalid;
}

int access_shm() {
  shmvalid = 0;
  for (int i = 0; i < 1000; i++) {
    if ((shmid = shmget(9000, 2 * sizeof(int), 0666)) == -1) {
      usleep(1000);
      continue;
    }
    shmvalid = 1;
    break;
  }
  if (!shmvalid) {
    return 0;
  }

  if ((values = (int *)shmat(shmid, nullptr, 0666)) == (int *) -1) {
    shmvalid = 0;
  }

  return shmvalid;
}

void deaccess_shm() {
  shmdt(values);
}

void delete_shm() {
  if (values != nullptr) {
    if (shmdt(values) == -1) {
      return;
    }
    // remove buf
    struct shmid_ds sds;
    shmctl(shmid, IPC_RMID, &sds);
    values = nullptr;
  }
}

int val0() {
  return values[0];
}

int val1() {
  return values[1];
}

void set_vals(int a, int b) {
  values[0] = a;
  values[1] = b;
}
