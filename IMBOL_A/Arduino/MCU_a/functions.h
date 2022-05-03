#ifndef FUNCTIONS_H
#define FUNCTIONS_H

/*****************************************
**************PINS DECLARING**************
******************************************/
#define P_CS A_CS //Pressure 4-20 ma current receiver ADC chip select (CS) pin
//define CS pin for both ADCs reading  the pt100
#define T1_CS C_CS //T_AMB
#define T2_CS D_CS //T_SURF


#define OVERFLOW_PIN      2

#define POT_CS            3

#define NEVER_USE_PIN     4

#define DOSING_VALVE_PIN  5
#define N2_VALVE_PIN      6
#define NOVEC_VALVE_PIN   7

#define PUMP_EN_PIN       8
#define PUMP_IN1_PIN      9
#define PUMP_IN2_PIN      10

#define WIPER_IN1_PIN     11
#define WIPER_IN2_PIN     12
#define WIPER_EN_PIN      13 

/*****************************************
**********STATE VARS AND TIMERS***********
******************************************/
uint8_t config_state=OVERFLOW_TRGD;//All valves closed, motors off and level sensor triggered for safety
bool wiper_state=false;
bool wiper_dir=true;
bool pump_state=false;


unsigned long now_measure;
unsigned long now_motors;
uint16_t T_AMB;
uint16_t T_SURF;

uint32_t P_total=0;
uint8_t  P_i=0;
const uint8_t  P_points=10;
uint16_t P_readings[P_points];
uint16_t P_ABS;

uint8_t adress;
uint8_t new_config_state;
uint8_t new_temp;

uint8_t PUMP_POWER_SET=128; //1 byte set for analogwrite for the motor power contol
uint8_t WIPER_POWER_SET=50; //1 byte set for analogwrite for the motor power contol
uint16_t dose_timer=500; // ms time for the solenoid to remain open during single dosing routine
unsigned long now_single_dose;

int ans;



/*****************************************
************Pressure constants************
******************************************/
float A_R=A_R1;
float B_R=B_R1;
float A_P=A_P1;
float B_P=B_P1;


/*****************************************
***************PID settings***************
******************************************/

double Kp = 2, Ki = 5, Kd = 1;
PID_v2 HEATER_PID(Kp, Ki, Kd, PID::Direct);
int T_SURFACE_SET=0;//C
double PID_output;
/*****************************************
**************PID set output**************
******************************************/
void set_POT(unsigned int data){
  uint8_t databyte=0;
  uint8_t cmdbyte=0b00010000;//which is for volatile memory wiper 1, in order to use wiper 0 use 0h00 instead
  if (data>255){
    cmdbyte|=0b00000001;
  }
  databyte=data & 0x00FF;
  SPI.beginTransaction(SPISettings(10000000, MSBFIRST, SPI_MODE0));
  digitalWrite(POT_CS, LOW);//We set the ADC CS pin to low to start receiving data
  SPI.transfer(cmdbyte);//We set the adress, write function and first data byte (all zero for the write case)
  SPI.transfer(databyte);//We ssend the data
  digitalWrite(POT_CS, HIGH);
  SPI.endTransaction();
}




/*****************************************
**************GET_PRESSURE****************
******************************************/
float get_pressure(int CS){
/*
 Tis function reads the 12 bit ADC output sent through SPI at chipselect pin CS. 
 Then converts to current using current calibration constants A_R and B_R, where R stands for receiver, 
 and finally converts to pressure from calibration constants A_P and B_P, where P stands for pressure. 
 The current convertion calibration constants for the receiver where obtained in the lab, using a high 
 quality multimeter. While the pressure calibration constants come from the sensor manufacturer. 
 The constant values can be found on the pressure_calibration.h header file 
*/
  byte first_byte;
  byte second_byte;
  unsigned int ADC_output;
  float current_output;
  float pressure_output;

  SPI.beginTransaction(SPISettings(1000000, MSBFIRST, SPI_MODE1)); //We initialize SPI comunication
  digitalWrite(CS, LOW); //We set the ADC CS pin to low to start receiving data
  //We receive 16 bits from the ADC in 2 bytes
  first_byte = SPI.transfer(0);
  second_byte = SPI.transfer(0);
  digitalWrite(CS, HIGH); //We set the ADC CS pin to high to stop receiving data
  SPI.endTransaction(); //finalize SPI comunication
/*The first byte contains 2 null bits, followed by  one low bit and the 5 most significant bits (see MCP3201 ADC datasheet) 
The second byte contains  the 7 less significant bits followed by B1 (which is a repeated bit) (see MCP3201 ADC datasheet)*/
 
  first_byte=first_byte<<2; //Shift to the left and pad with 0s to get rid of null bits 
  first_byte=first_byte>>2; //Shift to the right and pad with 0s to format the byte
  second_byte=second_byte>>1; //Shift to the right to get rid of the repeated B1 bit
 

  ADC_output = first_byte<<7| second_byte; //Fill the bits on the ADC output int variable 
  //current_output=A_R*ADC_output+B_R; //convert output to mA
  //pressure_output=A_P*current_output+B_P;// convert output to mbar
  //return pressure_output;
  return ADC_output;
}

/*****************************************
****************RTD_WRITE*****************
******************************************/
void write_RTD(uint8_t CS,uint8_t addr, uint8_t data){
  digitalWrite(CS, LOW);//We set the ADC CS pin to low to start receiving data
  SPI.transfer(addr);//We set the adress to write to
  SPI.transfer(data);//We ssend the data
  digitalWrite(CS, HIGH); //We set the ADC CS pin to high to stop receiving data
}

/*****************************************
****************RTD_READ******************
******************************************/
uint8_t read_RTD(uint8_t CS,uint8_t addr) {
  digitalWrite(CS, LOW);//We set the ADC CS pin to low to start receiving data
  SPI.transfer(addr);//We set the adress to read
  uint8_t ret = SPI.transfer(0); //We provide a dummy write to read  with clk cycles
  digitalWrite(CS, HIGH); //We set the ADC CS pin to high to stop receiving data
  return ret;
}

/*****************************************
****************GET_TEMP******************
******************************************/
int get_temp(int CS) {
  SPI.beginTransaction(SPISettings(1000000, MSBFIRST, SPI_MODE1)); //We initialize SPI comunication
  uint8_t LSB_byte=read_RTD(CS,RTD_LSB);
  uint8_t MSB_byte=read_RTD(CS,RTD_MSB);
//  write_RTD(CS,RTD_CONFIG_WRITE,ADC_READ);
  SPI.endTransaction();
  
  int ADC_output =  ((MSB_byte << 7)+((LSB_byte & 0xFE) >> 1));//Fill the bits on the ADC output int variable
  return ADC_output;
}
int temp2ADC(float T){

  float R = 1;
  R+=a*T;
  R+=b*T*T;
  R*=RNOMINAL;
  return int(R*32768/RREF);
}
float temp_C(int ADC_output) {
  float R_output=ADC_output*RREF/32768;//Obtain the resistance value of the RTD
  float Rrate=R_output/RNOMINAL;
  float temp_output=a*a;
  temp_output-=4*b*(1-Rrate);
  temp_output=sqrt(temp_output);
  temp_output-=a;
  temp_output/=2*b;
  return temp_output;
}
float get_temp_C(uint8_t CS) {
  int ADC_output = get_temp(CS);
  float temp_output = temp_C(ADC_output);
  return temp_output;
}

/*****************************************
*************measure****************
******************************************/


void measure(){
    
    if (digitalRead(D_INT)==LOW){
       T_SURF = get_temp(T2_CS);}
    if(digitalRead(C_INT)==LOW){
       T_AMB  = get_temp(T1_CS);}
    P_total=P_total-P_readings[P_i];
    P_readings[P_i]= get_pressure(P_CS);
    P_total=P_total+P_readings[P_i];
    P_i++;
    if(P_i==P_points){P_i=0;}
    P_ABS=P_total/P_points;
    //P_ABS=P_total;
  
}


/*****************************************
*************VALVE CONTROL****************
******************************************/

void close_valve(uint8_t pin){digitalWrite(pin,LOW);}
void open_valve(uint8_t pin){digitalWrite(pin,HIGH);}
void switch_valves(uint8_t state){
 digitalWrite(N2_VALVE_PIN,bitRead(state,0));
 digitalWrite(NOVEC_VALVE_PIN,bitRead(state,1));
 digitalWrite(DOSING_VALVE_PIN,bitRead(state,2));
 if(bitRead(state,7)){now_single_dose=millis();}

}
void check_overflow(){
  if (digitalRead(OVERFLOW_PIN)==LOW){
    close_valve(NOVEC_VALVE_PIN);
    config_state|=OVERFLOW_TRGD;
    config_state &= ~OPEN_NOVEC;
    switch_valves(config_state);
    
    
  }
  else {
    config_state &= ~OVERFLOW_TRGD;
  }
}


/*****************************************
*************SINGLE DOSE *****************
******************************************/
void single_dose_check(){
  if (bitRead(config_state,7) and (millis()-now_single_dose>dose_timer)){
    config_state &= ~(OPEN_DOSING|SINGLE_DOSE);
    switch_valves(config_state);
    }
}


/*****************************************
*************MOTORS CONTROL****************
******************************************/
void switch_motors(uint8_t state){
  
  wiper_state=bitRead(state,4);
  pump_state=bitRead(state,5);
  if(wiper_state==true){
    analogWrite(WIPER_EN_PIN,WIPER_POWER_SET);
  }
  else{
    analogWrite(WIPER_EN_PIN,0);
    }
  if(pump_state==true){
    analogWrite(PUMP_EN_PIN,PUMP_POWER_SET);
  }
  else{
    analogWrite(PUMP_EN_PIN,0);
    }
  
}

void check_wiper_dir(uint8_t state){
    wiper_dir=bitRead(state,6);
    digitalWrite(WIPER_IN1_PIN, !wiper_dir);
    digitalWrite(WIPER_IN2_PIN, wiper_dir);
    now_motors = millis(); 
}
#endif
