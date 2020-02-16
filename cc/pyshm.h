#pragma once

extern "C" {

int create_shm();
int access_shm();
void deaccess_shm();
void delete_shm();
int val0();
int val1();
int autonomous();
void set_vals(int steer, int speed, int _auto);

}
