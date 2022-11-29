#ifndef COMMUNICATION_H
#define COMMUNICATION_H

#define REGISTER_READ        0x00
#define REGISTER_WRITE       0x01
#define REGISTER_RTD1        0x02
#define REGISTER_RTD2        0x03
#define REGISTER_CONNECT     0x06


void serial(){
  uint8_t data;
  uint16_t data16;
  while (Serial.available() > 0) {
      
      uint8_t adress = Serial.read();
      switch (adress) {
        case REGISTER_READ:
        data16=round(P_EMA);
        Serial.write((data16>>8)&0xFF);
        Serial.write(data16&0xFF);
        for (int i = 0; i < sizeof(RTD)/sizeof(RTD[0]); i++){
          Serial.write((RTD[i]>>8)&0xFF);
          Serial.write(RTD[i]&0xFF);
        }
        
        break;
      case REGISTER_CONNECT:
        digitalWrite(LED_A,1);
        Serial.write("MCU_a\n");
        break;
      default:
        while (Serial.available() > 0) Serial.read();
        break;
        
     }
     
    }
}
#endif