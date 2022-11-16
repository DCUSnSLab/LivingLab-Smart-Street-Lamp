#include <stdio.h>
#include <wiringPi.h>

int btn = 21;
int led = 20;

int main(){
    wiringPiSetupGpio();
    pinMode(btn, INPUT);
    pinMode(led, OUTPUT);

    while(1){   
        if(digitalRead(btn)){
            digitalWrite(led, LOW);
            delay(10);
        } else {
            digitalWrite(led, HIGH);
            delay(100);
        }
    }
    return 0;
}