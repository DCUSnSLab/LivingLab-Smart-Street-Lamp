import time
import RPi.GPIO as GPIO

from gateway.procImpl import ProcessImpl


class EmergencyButton(ProcessImpl):
    def __init__(self, name):
        super().__init__(name)

    def doProc(self):
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(20, GPIO.OUT)
        GPIO.setup(21, GPIO.IN)

        try:
            while 1:
                inputIO = GPIO.input(21)
                # print('d', inputIO)

                if inputIO == False:
                    print('bell - Emergency State')
                    GPIO.output(20, True)
                    time.sleep(7)
                
                else:
                    # print('bell - Normal State')
                    time.sleep(1)
                GPIO.output(20, False)
        except KeyboardInterrupt:
            GPIO.cleanup()