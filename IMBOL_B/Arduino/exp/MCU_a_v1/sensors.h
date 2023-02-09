#ifndef SENSORS_H
#define SENSORS_H


/*****************************************
****************PRESSURE******************
******************************************/

#define P_CS        77 //change acordingly 

uint32_t P_EMA_interval = 2000;   // Desired oversampling interval [µs]
float P_EMA_LP_freq = 10e-6;      // Low-pass filter cut-off frequency [MHz]
float P_EMA = NAN;         // EMA output value [fractional bitval]
uint32_t P_EMA_tick = micros();   // Time of last oversampled reading [µs]

uint16_t P_get(){

  uint8_t first_byte;
  uint8_t second_byte;
  uint16_t ADC_output;


  SPI.beginTransaction(SPISettings(1000000, MSBFIRST, SPI_MODE1)); 
  digitalWrite(P_CS, LOW); 
  first_byte = SPI.transfer(0);
  second_byte = SPI.transfer(0);//One read needs 2 bytes
  digitalWrite(P_CS, HIGH); 
  SPI.endTransaction(); //finalize SPI comunication
/*The first byte contains 2 null bits, followed by  one low bit and the 5 most significant bits (see MCP3201 ADC datasheet) 
The second byte contains  the 7 less significant bits followed by B1 (which is a repeated bit) (see MCP3201 ADC datasheet)*/
  first_byte&= 0x1f; 
  second_byte>>=1; 
  ADC_output = first_byte<<7| second_byte; //Fill the bits on the ADC output int variable 
  return ADC_output;
}

void P_config(){
    delay(50);
    digitalWrite(P_CS, LOW);
    delay(100);
    digitalWrite(P_CS, HIGH);
    P_get();
}

bool P_poll_EMA() {
  uint32_t now = micros();
  float alpha; // Derived smoothing factor of the exponential moving average
  uint32_t EMA_obtained_interval; 

  if ((now - P_EMA_tick) >= P_EMA_interval) {
    // Enough time has passed -> Acquire a new reading.
    // Calculate the smoothing factor every time because an exact interval time
    // is not garantueed.
    EMA_obtained_interval = now - P_EMA_tick;
    alpha = 1.f - exp(-float(EMA_obtained_interval) * P_EMA_LP_freq);
    P_EMA += alpha * (P_get() - P_EMA);
    P_EMA_tick = now;
    return true;

  } else {
    return false;
  }
}


/*****************************************
**************TEMPERATURE*****************
******************************************/
#define RTD1_CS A4
#define RTD2_CS 4
#define RTD3_CS A2
#define RTD4_CS A3

uint8_t RTD_CS[]{RTD1_CS,RTD2_CS,RTD3_CS,RTD4_CS};
uint32_t RTD_tick = micros();
uint32_t RTD_interval = 21000;
uint16_t RTD[sizeof(RTD_CS)/sizeof(RTD_CS[0])]{};



#define RTD_CONFIG_READ 0x00
#define RTD_CONFIG_WRITE 0x80

#define RTD_BIAS 0x80
#define RTD_MODEAUTO 0x40
#define RTD_1SHOT 0x20
#define RTD_3WIRE 0x10
#define RTD_FAULTSTAT_READ 0x02
#define RTD_50HZ 0x01

#define RTD_MSB 0x01
#define RTD_LSB 0x02
#define RTD_HFAULTMSB 0x03
#define RTD_HFAULTLSB 0x04
#define RTD_LFAULTMSB 0x05
#define RTD_LFAULTLSB 0x06
#define RTD_FAULTSTAT 0x07

#define RTD_FAULT_HIGHTHRESH 0x80
#define RTD_FAULT_LOWTHRESH 0x40
#define RTD_FAULT_REFINLOW 0x20
#define RTD_FAULT_REFINHIGH 0x10
#define RTD_FAULT_RTDINLOW 0x08
#define RTD_FAULT_OVUV 0x04

SPISettings RTDSPI(1000000, MSBFIRST, SPI_MODE1);

uint8_t RTD_read(uint8_t CS,uint8_t addr) {
  
  SPI.beginTransaction(RTDSPI);
  digitalWrite(CS, LOW);
  SPI.transfer(addr);
  uint8_t data = SPI.transfer(0); 
  digitalWrite(CS, HIGH);
  SPI.endTransaction(); 
  return data;
}

void RTD_write(uint8_t CS,uint8_t addr, uint8_t data){
  SPI.beginTransaction(RTDSPI);
  digitalWrite(CS, LOW);//We set the ADC CS pin to low to start receiving data
  SPI.transfer(addr);//We set the adress to write to
  SPI.transfer(data);//We ssend the data
  digitalWrite(CS, HIGH); //We set the ADC CS pin to high to stop receiving data
  SPI.endTransaction();
}

void RTD_config(){
    for (int i = 0; i < sizeof(RTD_CS)/sizeof(RTD_CS[0]); i++)
    {
        delay(50);
        RTD_write(RTD_CS[i], RTD_CONFIG_WRITE, RTD_MODEAUTO|RTD_BIAS);
    }
}

uint16_t RTD_get(uint8_t CS) {
  uint8_t LSB_byte=RTD_read(CS,RTD_LSB);
  uint8_t MSB_byte=RTD_read(CS,RTD_MSB);
  uint16_t ADC_output =  ((MSB_byte << 7)+((LSB_byte & 0xFE) >> 1));//Fill the bits on the ADC output int variable
  return ADC_output;
}

void RTD_poll(){
  uint32_t now = micros();
  
  if ((now - RTD_tick) > RTD_interval) {
    // Enough time has passed -> Acquire a new reading.
    for (int i = 0; i < sizeof(RTD)/sizeof(RTD[0]); i++)
    {
        RTD[i]=RTD_get(RTD_CS[i]);
    }
    
    RTD_tick = now;

  } 

}



#endif