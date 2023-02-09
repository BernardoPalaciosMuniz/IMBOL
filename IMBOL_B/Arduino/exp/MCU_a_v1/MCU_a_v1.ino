#include <SPI.h>
#include <PID_v2.h>
double Kp1 = 2, Ki1 = 5, Kd1 = 1;
double Kp2 = 2, Ki2 = 5, Kd2 = 1;
PID_v2 HEATER_PID1(Kp1, Ki1, Kd1, PID::Direct);
PID_v2 HEATER_PID2(Kp2, Ki2, Kd2, PID::Direct);
#include "sensors.h"
#include "actuators.h"
#include "communication.h"


void setup() {
  Serial.begin(9600);
  SPI_init();
  P_EMA = P_get();
  PID_config();
  pinMode(float_IN,INPUT);
  pinMode(DO_1,OUTPUT);
  digitalWrite(DO_1, HIGH);
  pinMode(DO_2,OUTPUT);
  digitalWrite(DO_2, HIGH);
  rel_W(REL_set,0xff);
}

void loop() {


  P_poll_EMA();
  RTD_poll();
  PID_run();
  trig_poll();
  dose_poll();
  serial();
  
}

void SPI_init(){
    int CSs[] { REL_CS, P_CS,RTD1_CS,RTD2_CS,RTD3_CS,RTD4_CS,DAC1_CS,DAC2_CS};

    SPI.begin();
    for (int i = 0; i < sizeof(CSs)/sizeof(CSs[0]); i++)
    {
        pinMode(CSs[i], OUTPUT);
        digitalWrite(CSs[i], HIGH);
    }

    P_config();
    RTD_config();
    rel_config();
}
void dose_poll(){
  if(DOSE_single){
    uint32_t now=millis();
    if (now-DOSE_tick>=DOSE_int)
    {
    uint8_t data=~REL_8;
    data|=rel_R(REL_set);
    rel_W(REL_set,data);
    DOSE_single=0;
    }
    
  }
}