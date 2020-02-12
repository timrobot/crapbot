#pragma pyshm_h

extern "C" {

int create_shm();
int access_shm();
void deaccess_shm();
void delete_shm();
int val0();
int val1();
void set_vals(int a, int b);

}
