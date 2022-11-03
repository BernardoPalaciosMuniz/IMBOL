#ifndef PRESSURE_H
#define PRESSURE_H
float A_R1=0.00251428;//Current calibration constant A for the 4-20 ma receiver labeled as 1
float B_R1=0.10016;//Current calibration constant B for the 4-20 ma receiver labeled as 1
float P_Range=1000;//Preasure range in mbar from calibration on provided sensor documentation
float I_Span_P1=15.998;// Current span in mA for sensor 1 from calibration on provided sensor documentation
float I0_P1=4.001;//Current at 0 mbar from calibration on provided sensor documentation
float A_P1= P_Range/I_Span_P1;
float B_P1= -A_P1*I0_P1;



#endif
