#include "motors.h"
#include "communication.h"

void setup() {  
    Serial.begin(9600);
    while (!Serial) {}
    for (uint8_t i = 1; i < 5; i++)
    {
        pinMode(motor_pins[i], OUTPUT);

    }
    pinMode(LED_BUILTIN,OUTPUT);
    motors(0);

}

void loop(){
  serial();
  }
