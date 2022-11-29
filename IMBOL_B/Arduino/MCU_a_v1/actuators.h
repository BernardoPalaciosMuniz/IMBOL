#ifndef ACTUATORS_H
#define ACTUATORS_H


/*****************************************
*************RELAYS****************
******************************************/

#define REL_CS      A1
#define relread     0x41
#define relwrite    0x40
#define REL_config  0x00
#define REL_set     0x0A
#define REL_1 0x01 //MAIN
#define REL_2 0x02 //VACUUM
#define REL_3 0x04 //N2
#define REL_4 0x08 //N7000
#define REL_5 0x10 //DOSING
#define REL_6 0x20 //RETRIEVE
#define REL_8 0x80 //LIGHT

SPISettings relSPI(10000000, MSBFIRST, SPI_MODE0);

void rel_W(uint8_t adress, uint8_t data)
{
  uint8_t control=relwrite;
  digitalWrite(REL_CS, LOW);
  SPI.beginTransaction(relSPI);
  SPI.transfer(control);
  SPI.transfer(adress);
  SPI.transfer(data);
  SPI.endTransaction();
  digitalWrite(REL_CS, HIGH);
}
uint8_t rel_R(uint8_t adress)
{
  uint8_t data;
  uint8_t control=relread;
  digitalWrite(REL_CS, LOW);
  SPI.beginTransaction(relSPI);
  SPI.transfer(control);
  SPI.transfer(adress);
  data=SPI.transfer(0x00);
  SPI.endTransaction();
  digitalWrite(REL_CS, HIGH);
  return data;
}

void rel_config()
{
  digitalWrite(REL_CS, LOW);
  SPI.beginTransaction(relSPI);
  SPI.transfer(relwrite);
  SPI.transfer(REL_config);
  for (int i = 0x00; i < 0x0A; i++){SPI.transfer(0x00);}
  SPI.transfer(0xff);
  SPI.endTransaction();
  digitalWrite(REL_CS, HIGH);
}

/*****************************************
******************D.O.********************
******************************************/
#define DO_1  12
#define DO_2  11
uint32_t trig_tick=millis();
uint32_t trig_period=6000;
uint8_t trig_bit=0;
void lights_on(){
  digitalWrite(DO_2,LOW);
  uint8_t data;
  data=rel_R(REL_set);
  data&=~REL_8;
  rel_W(REL_set,data);

}
void lights_off(){
  digitalWrite(DO_2,HIGH);
  uint8_t data;
  data=rel_R(REL_set);
  data|=REL_8;
  rel_W(REL_set,data);
}
void trig(){
  digitalWrite(DO_1,LOW);
  trig_tick=millis();
  trig_bit=1;
}
void trig_poll(){
  if(trig_bit){
    if((millis()-trig_tick)>trig_period){
      digitalWrite(DO_1,HIGH);
      trig_bit=0;
      lights_off();
    }
  }
}




/*****************************************
******************DOSE********************
******************************************/
uint32_t DOSE_int=500;
uint32_t DOSE_tick=millis();
bool DOSE_single=0;



/*****************************************
**************FLOAT SWITCH****************
******************************************/
#define float_IN 13
void floatswitch(){
    if (!digitalRead(float_IN)){
        uint8_t data=rel_R(REL_set);
        data|=REL_4;
        rel_W(REL_set,data);
    }

}

/*****************************************
*****************HEATERS******************
******************************************/

#define DAC1_CS   5
#define DAC2_CS   6


void set_DAC(uint8_t cs,uint16_t value) //mcp4921
{
  uint16_t data = 0x3000 | value;
  SPI.beginTransaction(SPISettings(10000000, MSBFIRST, SPI_MODE0));
  digitalWrite(cs, LOW);
  SPI.transfer((uint8_t)(data >> 8));
  SPI.transfer((uint8_t)(data & 0xFF));
  SPI.endTransaction();
  digitalWrite(cs, HIGH);
}

/*****************************************
********************PID*******************
******************************************/
#define T0 0
float RREF=470;
float RNOMINAL=100.0;
float a=0.00390830;
float b=-0.0000005775;
int temp2ADC(float T){
  float R = 1;
  R+=a*T;
  R+=b*T*T;
  R*=RNOMINAL;
  return int(R*32768/RREF);
// double Kp = 2, Ki = 5, Kd = 1;
// PID_v2 HEATER_PID1(Kp, Ki, Kd, PID::Direct);
// PID_v2 HEATER_PID2(Kp, Ki, Kd, PID::Direct);


}

void PID_config(){
  HEATER_PID1.SetOutputLimits(0, 0xFFF);//0 to full scale on the DAC (12bits)
  HEATER_PID1.Start(RTD_get(RTD1_CS), 0, temp2ADC(T0));
  HEATER_PID2.SetOutputLimits(0, 0xFFF);//0 to full scale on the DAC (12bits)
  HEATER_PID2.Start(RTD_get(RTD2_CS), 0, temp2ADC(T0));

 }

 void PID_run(){
  uint16_t DAC1_set=HEATER_PID1.Run(RTD[0]);
  set_DAC(DAC1_CS,DAC1_set);
  uint16_t DAC2_set=HEATER_PID2.Run(RTD[1]);
  set_DAC(DAC2_CS,DAC2_set);
 }
#endif
