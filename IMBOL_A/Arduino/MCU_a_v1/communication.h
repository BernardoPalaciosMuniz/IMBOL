#ifndef COMMUNICATION_H
#define COMMUNICATION_H

#define REGISTER_READ       0x00
#define REGISTER_WRITE      0x01
#define REGISTER_RTD1       0x02
#define REGISTER_RTD2       0x03
#define REGISTER_DOSE_T     0x04
#define REGISTER_DOSE_S     0x05
#define REGISTER_CONNECT    0x06
#define REGISTER_TOGGLE     0x07
#define REGISTER_TRIGGER    0x08
#define REGISTER_LIGHTSON   0x09
#define REGISTER_LIGHTSOFF  0x0A

void serial(){
  uint8_t data;
  uint16_t data16;
  while (Serial.available() > 0) {
      uint8_t adress = Serial.read();
      switch (adress) {
        case REGISTER_READ:
        data16=round(P_EMA);
        Serial.write(~rel_R(REL_set));
        Serial.write((digitalRead(float_IN))&0x1);
        Serial.write((data16>>8)&0xFF);
        Serial.write(data16&0xFF);
        for (int i = 0; i < sizeof(RTD)/sizeof(RTD[0]); i++){
          Serial.write((RTD[i]>>8)&0xFF);
          Serial.write(RTD[i]&0xFF);
        }
        data16=HEATER_PID1.Run(RTD[0]);
        Serial.write((data16>>8)&0xFF);
        Serial.write(data16&0xFF);
        data16=HEATER_PID2.Run(RTD[1]);
        Serial.write((data16>>8)&0xFF);
        Serial.write(data16&0xFF);
        
        break;
      case REGISTER_WRITE:
        while (Serial.available() == 0) {}
        data = Serial.read();
        rel_W(REL_set,~data);
        break;
      case REGISTER_TOGGLE:
        data=rel_R(REL_set);
        while (Serial.available() == 0) {}
        data ^=Serial.read();
        rel_W(REL_set,data); 
        break;
     case REGISTER_RTD1:
       while (Serial.available() == 0) {}
       data16=(Serial.read()<<8)&0xFF00;
       while (Serial.available() == 0) {}
       data16|=(Serial.read())&0x00FF;
       HEATER_PID1.Setpoint(data16);
       data16=HEATER_PID1.GetSetpoint();
       Serial.write((data16 >> 8)  & 0xFF);
       Serial.write(data16 & 0xFF);
       break;
     case REGISTER_RTD2:
       while (Serial.available() == 0) {}
       data16=(Serial.read()<<8)&0xFF00;
       while (Serial.available() == 0) {}
       data16|=(Serial.read())&0x00FF;
       HEATER_PID2.Setpoint(data16);
       data16=HEATER_PID2.GetSetpoint();
       Serial.write((data16 >> 8)  & 0xFF);
       Serial.write(data16 & 0xFF);
       break;
      case REGISTER_DOSE_T:
        while (Serial.available() == 0) {}
        data16=(Serial.read()<<8)&0xFF00;
        while (Serial.available() == 0) {}
        data16|=(Serial.read())&0x00FF;
        DOSE_int=data16;
        Serial.write((data16 >> 8)  & 0xFF);
        Serial.write(data16 & 0xFF);
        break;
      case REGISTER_DOSE_S:
        data=(~REL_5);
        rel_W(REL_set,data);
        DOSE_single=1;
        DOSE_tick=millis();
        break;
      case REGISTER_LIGHTSON:
        lights_on();
        break;
      case REGISTER_LIGHTSOFF:
        lights_off();
        break;
      case REGISTER_TRIGGER:
        data=REL_5;
        data|=REL_8;
        rel_W(REL_set,~data);
        DOSE_single=1;
        DOSE_tick=millis();
        trig();
        data16=round(P_EMA);
        Serial.write((data16>>8)&0xFF);
        Serial.write(data16&0xFF);
        for (int i = 0; i < sizeof(RTD)/sizeof(RTD[0]); i++){
          Serial.write((RTD[i]>>8)&0xFF);
          Serial.write(RTD[i]&0xFF);
        }
        break;
      case REGISTER_CONNECT:
        Serial.write("MCU_a\n");
        break;
      default:
        while (Serial.available() > 0) Serial.read();
        break;
        
     }
     
    }
}
#endif