#include <SPI.h>

#include "board_header.h"
#include "sensors.h"
#include "communication.h"


void setup() {
  pinMode(LED_A,OUTPUT);
  pinMode(LED_B,OUTPUT);
  pinMode(LED_C,OUTPUT);
  pinMode(LED_D,OUTPUT);
  digitalWrite(LED_A,0);
  digitalWrite(LED_B,0);

  Serial.begin(200000);
  SPI_init();
  P_EMA = P_get();
  
}

void loop() {


  P_poll_EMA();
  RTD_poll();
  serial();
  
}

void SPI_init(){
    int CSs[] { P_CS,RTD1_CS,RTD2_CS};

    SPI.begin();
    for (int i = 0; i < sizeof(CSs)/sizeof(CSs[0]); i++)
    {
        pinMode(CSs[i], OUTPUT);
        digitalWrite(CSs[i], HIGH);
    }

    P_config();
    RTD_config();

}
