#include <SPI.h>

#include "board_header.h"
#include "sensors.h"

void setup() {


  /**********************************************************
    Initialize the pressure sensor ADC spi communication, as
    instructed on the datasheet of the onboard MCP3201 ADC
  ***********************************************************/

  pinMode (P_CS, OUTPUT);
  digitalWrite(P_CS, HIGH);
  delay(100);
  digitalWrite(P_CS, LOW);
  delay(100);
  /**********************************************************
    Start comunicaction
  ***********************************************************/
  SPI.begin();
  Serial.begin(9600);
  Serial.write("BOLI");

  /**********************************************************
    Set inputs and outputs and set CS pins to HIGH
  ***********************************************************/


  digitalWrite(P_CS, HIGH);




  /**********************************************************
    Initialize the PID controller and the timer from the output
    //TC1 channel 0, the IRQ for that channel and the desired
    frequency. This timer is currently not used
  ***********************************************************/
  
///  HEATER_PID.SetOutputLimits(0, 256);//0 to full scale on the digital potentiometer
//  HEATER_PID.Start(get_temp(T1_CS), 0, temp2ADC(T_SURFACE_SET));


  //startTimer(TC1, 0, TC3_IRQn, 100);


  /**********************************************************
    Set the configuration of the temperature sensors and get
    pressure once, ussually the first read is faulty
  ***********************************************************/
  get_pressure(P_CS);
  delay(50);

  
  

  

}

void loop() {
  Serial.println(get_pressure(P_CS));
  delay(1000);


  

  

}
