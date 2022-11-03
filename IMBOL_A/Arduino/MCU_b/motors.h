
#define IN1   7 
#define IN2   5 
#define IN3   4 
#define IN4   2 

#define ENA   6 
#define ENB   3 
uint8_t motors_config=0;
uint8_t MOTORA_SET=200;
uint8_t MOTORB_SET=200;
uint8_t motor_pins[]{ENA, IN1, IN2, IN3, IN4, ENB};

uint8_t motors(uint8_t motors_config){
    uint8_t PWMA=bitRead(motors_config,0)*MOTORA_SET;
    uint8_t dirA=bitRead(motors_config,1);
    digitalWrite(IN1, dirA);
    digitalWrite(IN2, !dirA);
    analogWrite(ENA,PWMA);

    uint8_t PWMB=bitRead(motors_config,2)*MOTORB_SET;
    uint8_t dirB=bitRead(motors_config,3);
    digitalWrite(IN3, dirB);
    digitalWrite(IN4, !dirB);
    analogWrite(ENB,PWMB);
return motors_config;
}