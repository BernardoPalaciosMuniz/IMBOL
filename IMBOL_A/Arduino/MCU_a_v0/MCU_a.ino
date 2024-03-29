#include <SPI.h>
#include <PID_v2.h>
#include "board_header.h"
#include "pressure.h" //inlcude the calibration data, this variables can be read on the header file
#include "temperature.h"
#include "serial_registers.h"
#include "functions.h"

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
  Serial.write("IMBOL_A_MCU_a\n");

  /**********************************************************
    Set inputs and outputs and set CS pins to HIGH
  ***********************************************************/
  pinMode (T1_CS, OUTPUT);
  digitalWrite(T1_CS, HIGH);
  pinMode (T2_CS, OUTPUT);
  digitalWrite(T2_CS, HIGH);
  pinMode (POT_CS, OUTPUT);
  digitalWrite(POT_CS, HIGH);
  digitalWrite(P_CS, HIGH);
  pinMode (C_INT, INPUT);
  pinMode (D_INT, INPUT);


  pinMode(N2_VALVE_PIN, OUTPUT);
  pinMode(NOVEC_VALVE_PIN, OUTPUT);
  pinMode(DOSING_VALVE_PIN, OUTPUT);
  pinMode(OVERFLOW_PIN, INPUT_PULLUP);
  pinMode(PUMP_IN1_PIN, OUTPUT);
  pinMode(PUMP_IN2_PIN, OUTPUT);
  pinMode(WIPER_IN1_PIN, OUTPUT);
  pinMode(WIPER_IN2_PIN, OUTPUT);
  pinMode(LED_A, OUTPUT);
  pinMode(LED_B, OUTPUT);
  pinMode(LED_C, OUTPUT);
  pinMode(LED_D, OUTPUT);

  switch_motors(config_state);


  /**********************************************************
    Initialize the PID controller and the timer from the output
    //TC1 channel 0, the IRQ for that channel and the desired
    frequency. This timer is currently not used
  ***********************************************************/
  
  HEATER_PID.SetOutputLimits(0, 256);//0 to full scale on the digital potentiometer
  HEATER_PID.Start(get_temp(T1_CS), 0, temp2ADC(T_SURFACE_SET));


  //startTimer(TC1, 0, TC3_IRQn, 100);


  /**********************************************************
    Set the configuration of the temperature sensors and get
    pressure once, ussually the first read is faulty
  ***********************************************************/
  delay(50);
  SPI.beginTransaction(SPISettings(1000000, MSBFIRST, SPI_MODE1));
  write_RTD(T1_CS, RTD_CONFIG_WRITE, RTD_MODEAUTO|RTD_BIAS);
  write_RTD(T2_CS, RTD_CONFIG_WRITE, RTD_MODEAUTO|RTD_BIAS);
  SPI.endTransaction();
  get_pressure(P_CS);
  now_measure = micros();
  delay(50);
  digitalWrite(PUMP_IN1_PIN,LOW);
  digitalWrite(PUMP_IN2_PIN,HIGH);
  digitalWrite(WIPER_IN1_PIN, wiper_dir);
  digitalWrite(WIPER_IN2_PIN, !wiper_dir);
  
  

  

}

void loop() {

  check_overflow();
  
  measure();
  PID_output = HEATER_PID.Run(T_SURF);
  set_POT(PID_output);
  single_dose_check();
  


  if (Serial.available() > 0) {
    adress = Serial.read();
    switch (adress) {
      case CONFIG_READ:
        Serial.write(config_state);
        break;
      case CONFIG_WRITE:
        while (Serial.available() == 0) {}
        new_config_state = Serial.read();
        config_state = new_config_state;
        check_overflow();
        switch_valves(config_state);
        check_wiper_dir(config_state);
        switch_motors(config_state);
        Serial.write(config_state);
        break;
      case SENSORS_READ:
        Serial.write((T_AMB >> 8)  & 255);
        Serial.write(T_AMB & 255);
        Serial.write((T_SURF >> 8)  & 255);
        Serial.write(T_SURF & 255);
        Serial.write((P_ABS >> 8)  & 255);
        Serial.write(P_ABS & 255);
        break;
      case TEMP_SURF_WRITE:
        while (Serial.available() == 0) {}
        T_SURFACE_SET=Serial.read();
        HEATER_PID.Setpoint(temp2ADC(T_SURFACE_SET));
        ans=HEATER_PID.GetSetpoint();
        Serial.write((ans >> 8)  & 255);
        Serial.write(ans & 255);
        break;
      case DOSE_INTERVAL_WRITE:
        while (Serial.available() == 0) {}
        dose_timer=Serial.read()<<8;
        while (Serial.available() == 0) {}
        dose_timer+=Serial.read();
        Serial.write((dose_timer >> 8)  & 255);
        Serial.write(dose_timer & 255);
        break;
        
    }
    while (Serial.available() > 0) Serial.read();
  }

  

}
