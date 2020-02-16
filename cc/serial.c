#include <termios.h>
#include <sys/ioctl.h>
#include <sys/types.h>
#include <sys/wait.h>
#include <unistd.h>
#include <stdlib.h>
#include <string.h>
#include <fcntl.h>
#include <dirent.h>
#include <stdio.h>
#include <time.h>
#include "serial.h"

#include <stdint.h>

#define SWBUFMAX    1024
#define SWREADMAX   512
#define SWWRITEMAX  512

typedef struct serial {
  char    *port;
  int     fd;
  int8_t  connected;
  int     baudrate;
  int     parity;

  /* values */
  char    buffer[SWBUFMAX];
  char    readbuf[SWREADMAX];
  int8_t  readAvailable;
} serial_t;

serial_t arduino;
char writemsg[SWWRITEMAX];

#define INPUT_DIR "/dev/"
static const char *PREFIXES[] = { "ttyACM", NULL };
static int _serial_setattr(serial_t *connection);
static void _serial_update(serial_t *connection);
static char tempbuf[SWREADMAX];
static char interbuf[SWWRITEMAX];

/** Connect to a serial device.
 *  @param connection
 *    a pointer to the serial struct
 *  @param port
 *    a portname; if NULL, will open a random port
 *  @param baudrate
 *    the bits per second of information to transmit/receive
 *  @return 0 on success, -1 on failure
 */
int serial_connect(serial_t *connection, const char *port, int baudrate) {
  struct timespec t;
  connection->connected = 0;
  if (port) {
    connection->port = (char *)malloc((strlen(port) + 1) * sizeof(char));
    strcpy(connection->port, port);

    if ((connection->fd = open(connection->port, O_RDWR)) == -1) {
      goto error;
    }
  } else {
    DIR *dp;
    struct dirent *ent;
    char hasPossibleSerial;

    if (!(dp = opendir(INPUT_DIR))) {
      fprintf(stderr, "Cannot find directory %s to open serial connection\n",
          INPUT_DIR);
      return -1;
    }

    while ((ent = readdir(dp))) {
      const char *prefix;
      int i;
      hasPossibleSerial = 0;
      for (prefix = PREFIXES[(i = 0)]; prefix != NULL; prefix = PREFIXES[++i]) {
        if (strstr(ent->d_name, prefix)) {
          connection->port = (char *)malloc((strlen(INPUT_DIR) +
                strlen(ent->d_name) + 1) * sizeof(char));
          sprintf(connection->port, "%s%s", INPUT_DIR, ent->d_name);

          if ((connection->fd = open(connection->port,
                  O_RDWR | O_NONBLOCK)) == -1) {
            free(connection->port);
            connection->port = NULL;
          } else {
            hasPossibleSerial = 1;
            break;
          }
        }
      }

      if (hasPossibleSerial) {
        break;
      }
    }

    if (!hasPossibleSerial) {
      fprintf(stderr, "Cannot find a serial device to open\n");
      return -1;
    }
  }

  /* set connection attributes */
  connection->baudrate = baudrate;
  connection->parity = 0;

  if (_serial_setattr(connection) == -1) {
    goto error; /* possible bad behavior */
  }

  connection->connected = 1;
  memset(connection->buffer, 0, SWBUFMAX);
  memset(connection->readbuf, 0, SWREADMAX);
  connection->readAvailable = 0;

  /* Get rid of garbage (time: 900msec)
   */
  t.tv_sec = 0;
  t.tv_nsec = 900000000;
  nanosleep(&t, NULL);
  tcflush(connection->fd, TCIOFLUSH);

  return 0;

error:
  fprintf(stderr, "Cannot connect to the device on %s\n", connection->port);
  connection->connected = 0;

  if (connection->fd != -1) {
    close(connection->fd);
  }
  connection->fd = -1;

  if (connection->port) {
    free(connection->port);
  }

  connection->port = NULL;
  return -1;
}

/** Helper method to set the attributes of a serial connection,
 *  particularly for the arduino or similar device.
 *  @param connection
 *    the serial port to connect to
 *  @return 0 on success, -1 on failure
 */
static int _serial_setattr(serial_t *connection) {
  struct termios tty;

  if (tcgetattr(connection->fd, &tty) == -1) {
    return -1;
  }

  speed_t baud = B9600;
  switch (connection->baudrate) {
    case 4800:    baud = B4800;   break;
    case 9600:    baud = B9600;   break;
#ifdef B14400
    case 14400:   baud = B14400;  break;
#endif
    case 19200:   baud = B19200;  break;
#ifdef B28800
    case 28800:   baud = B28800;  break;
#endif
    case 38400:   baud = B38400;  break;
    case 57600:   baud = B57600;  break;
    case 115200:  baud = B115200; break;
  }
  cfsetospeed(&tty, baud);
  cfsetispeed(&tty, baud);

  // set new attributes
  tty.c_cflag &= ~PARENB;
  tty.c_cflag &= ~CSTOPB;
  tty.c_cflag &= ~CSIZE;
  tty.c_cflag |= CS8;
  tty.c_cflag &= ~CRTSCTS;
  tty.c_cflag |= CREAD | CLOCAL;
  tty.c_iflag &= ~(IXON | IXOFF | IXANY);
  tty.c_lflag &= ~(ICANON | ECHO | ECHOE | ISIG);
  tty.c_oflag &= ~OPOST;
  tty.c_cc[VMIN] = 0;
  tty.c_cc[VTIME] = 0;

  if (tcsetattr(connection->fd, TCSANOW, &tty) == -1) {
    return -1;
  }
  if (tcsetattr(connection->fd, TCSAFLUSH, &tty) == -1) {
    return -1;
  }
  return 0;
}

/** Method to update the readbuf of the serial communication,
 *  as well as the connection itself.
 *  @param connection
 *    the serial struct
 *  @note
 *    the packets will be read in the following format:
 *    data\n
 */
static void _serial_update(serial_t *connection) {
  int bytesRead;
  int bytesStored;
  unsigned char analyzeBuffer;

  /* dynamically reconnect the device */
  if (access(connection->port, F_OK) == -1) {
    if (connection->connected) {
      connection->connected = 0;
      connection->fd = -1;
    }
  } else {
    if (!connection->connected) {
      if ((connection->fd = open(connection->port,
              O_RDWR | O_NOCTTY | O_NDELAY)) != -1) {
        if (_serial_setattr(connection) == 0) {
          connection->connected = 1;
        } else {
          close(connection->fd);
          connection->fd = -1;
        }
      }
    }
  }

  if (!connection->connected) {
    return;
  }

  /* update buffer constantly (be careful of overflow!) */
  analyzeBuffer = 0;
  while ((bytesRead = read(connection->fd, tempbuf, SWREADMAX - 1)) > 0) {
    if (bytesRead > 0) {
      analyzeBuffer = 1; /* turn on buffer analysis signal */
    }
    tempbuf[bytesRead] = '\0';
    bytesStored = strlen(connection->buffer); /* no \0 */

    while (bytesStored + bytesRead >= SWBUFMAX) {
      /* shorten it by only half of the readmax value */
      bytesStored -= SWREADMAX / 2;
      memmove(connection->buffer, &connection->buffer[SWREADMAX / 2],
          bytesStored * sizeof(char));
      connection->buffer[bytesStored] = '\0';
    }

    strcat(connection->buffer, tempbuf);
  }

  if (analyzeBuffer) {
    char *end_index;
    if ((end_index = strchr(connection->buffer, '\n'))) {
      end_index[0] = '\0';
      end_index = &end_index[1];
      strcpy(connection->readbuf, connection->buffer);
      memmove(connection->buffer, end_index,
          (strlen(end_index) + 1) * sizeof(char));
      connection->readAvailable = 1;
    }
  }
}

/** Read a string from the serial communication link.
 *  @param connection
 *    the serial connection to read a message from
 *  @return the readbuf if a message exists, else NULL
 */
char *serial_read(serial_t *connection) {
  _serial_update(connection);
  if (connection->readAvailable) {
    connection->readAvailable = 0;
    return connection->readbuf;
  } else {
    return NULL;
  }
}

/** Write a message to the serial communication link.
 *  @param connection
 *    the serial communication link to write to
 *  @param message
 *    the message to send over to the other side
 */
void serial_write(serial_t *connection, const char *message) {
  if (connection->fd != -1) {
    //sprintf(interbuf, "%s", message);
    /* sending a null terminated string causes error, so just send length */
    if (write(connection->fd, message, strlen(interbuf)) != -1) {
      //printf("[SERIAL] write [%s][%zu]: %s\n",
      //    connection->port, strlen(interbuf) + 1, interbuf);
    }
  }
}

/** Disconnect from the USB Serial port.
 *  @param connection
 *    A pointer to the serial struct.
 */
void serial_disconnect(serial_t *connection) {
  /* clean up */
  if (!connection->connected) {
    return;
  }
  if (connection->fd != -1) {
    close(connection->fd);
  }
  if (connection->port != NULL) {
    free(connection->port);
  }
  memset(connection, 0, sizeof(serial_t));
  connection->fd = -1;
}

int rccar_connect(void) {
  memset(writemsg, 0, sizeof(writemsg));
  return serial_connect(&arduino, NULL, 57600);
}

void rccar_write(int steer, int speed) {
  writemsg[0] = steer;
  writemsg[1] = speed | 0x80;
  serial_write(&arduino, writemsg);
}

void rccar_disconnect(void) {
  serial_disconnect(&arduino);
}
