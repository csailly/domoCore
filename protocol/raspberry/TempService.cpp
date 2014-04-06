#include "TempService.h"
#include <errno.h>
#include <string.h>
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <linux/i2c-dev.h>
#include <sys/ioctl.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <fcntl.h>


#define TMP102_I2C	0x48
#define I2C_BUS		"/dev/i2c-1"

float TempService::getTemp(){

    int file;
    char filename[40];
    int addr = TMP102_I2C; // The I2C address

    sprintf(filename, I2C_BUS);
    if ((file = open(filename, O_RDWR)) < 0) {
		printf("Failed to open the bus.");
        /* ERROR HANDLING; you can check errno to see what went wrong */
        printf("error: %s (%d)\n", strerror(errno), errno);
        return 999.0;
    }

    if (ioctl(file, I2C_SLAVE, addr) < 0) {
		printf("Failed to acquire bus access and/or talk to slave.\n");
        /* ERROR HANDLING; you can check errno to see what went wrong */
        printf("error: %s (%d)\n", strerror(errno), errno);
        return 999.0;
    }

    write(file, 0x00, 1);

    usleep(500);
        
    char buf[1] = { 0 };

    float data;

    // Read 2 uint8 using I2C Read
    int k = read(file, buf, 2);
    if ((k != 2)) {
		printf("error: %s (%d)\n", strerror(errno), errno);
    } else {
		int temperature;

        temperature = ((buf[0]) << 8) | (buf[1]);
        temperature >>= 4;

        //The tmp102 does twos compliment but has the negative bit in the wrong spot, so test for it and correct if needed
        if (temperature & (1 << 11))
			temperature |= 0xF800; //Set bits 11 to 15 to 1s to get this reading into real twos compliment
		return temperature * 0.0625;
	}
    usleep(5);        
    return 999.9;
}