#ifndef COMMUNICATION_H
#define COMMUNICATION_H



#define REGISTER_WRITE      0x00
#define REGISTER_CONNECT    0x06
#define REGISTER_TOGGLE     0x02

void serial(){
  uint8_t data;
  if (Serial.available()>0) {
      uint8_t adress = Serial.read();
      switch (adress) {
      case REGISTER_WRITE:
        while (Serial.available() == 0) {}
        data = Serial.read();
        motors_config=motors(data);
        break;
      case REGISTER_TOGGLE:
        while (Serial.available() == 0) {}
        data = Serial.read();
        data=motors_config ^data;
        motors_config=motors(data);
        break;
     
      case REGISTER_CONNECT:
        digitalWrite(LED_BUILTIN,HIGH);
        Serial.write("MCU_b\n");
        break;
      default:
        while (Serial.available() > 0) Serial.read();
        break;
        
     }
     
    }
}
#endif
