
#define IN1   7 
#define IN2   5 
#define IN3   4 
#define IN4   2 

#define ENA   6 
#define ENB   3 
uint8_t motors_config=0;
uint8_t motor_pins[]{ENA, IN1, IN2, IN3, IN4, ENB};

uint8_t motors(uint8_t motors_config){
    uint8_t onA=bitRead(motors_config,0);
    uint8_t dirA=bitRead(motors_config,1);
    digitalWrite(IN1, dirA);
    digitalWrite(IN2, !dirA);
    digitalWrite(ENA,onA);

    uint8_t onB=bitRead(motors_config,2);
    uint8_t dirB=bitRead(motors_config,3);
    digitalWrite(IN3, dirB);
    digitalWrite(IN4, !dirB);
    digitalWrite(ENB,onB);
return motors_config;
}