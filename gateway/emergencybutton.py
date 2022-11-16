import time
import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BCM)
GPIO.setup(20, GPIO.OUT)
GPIO.setup(21, GPIO.IN)

try:
    while 1:
        inputIO = GPIO.input(21)
        # print('d', inputIO)

        if inputIO == False:
            print('Emergency State')
            GPIO.output(20, True)
            time.sleep(1)
        
        else:
            print('Normal State')
            time.sleep(0.5)
        GPIO.output(20, False)
except KeyboardInterrupt:
    GPIO.cleanup()
