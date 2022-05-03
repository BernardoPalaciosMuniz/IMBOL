#ifndef SERIAL_REGISTERS_H
#define SERIAL_REGISTERS_H

#define CONFIG_READ     0b00000000 //R
#define CONFIG_WRITE    0b10000000 //R

#define OPEN_N2         0b00000001 // B0 bit of the CONFIG adress is the state of the N2 valve
#define OPEN_NOVEC      0b00000010 // B1 bit of the CONFIG adress is the state of the NOVEC valve
#define OPEN_DOSING     0b00000100 // B2 bit of the CONFIG adress is the state of the dosing valve
#define OVERFLOW_TRGD   0b00001000 // B3 bit of the CONFIG adress is the state of overflow sensor
#define WIPER_ON        0b00010000 // B4 bit of the CONFIG adress is the state of wiper
#define PUMP_ON         0b00100000 // B5 bit of the CONFIG adress is the state of pump

#define SENSORS_READ   0b00000001 //R
#define TEMP_SURF_WRITE 0b10000001 //W


#endif
