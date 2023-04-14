import time
import RPi.GPIO as GPIO
import paho.mqtt.client as mqtt
import paho.mqtt.publish as publish
import json
import datetime as dt

from gateway.procImpl import ProcessImpl
from ota.type_definitions import *


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
                    x = dt.datetime.now()
                    json_object = {
                        "sh_id": SH_ID,
                        "lamp_id": LAMP_ID,
                        "datetime": x.strftime("%Y%m%d%H%M%S"),
                        "type": "2",
                        "info": {
                            "event": "4",
                        },
                    }
                    json_string = json.dumps(json_object)

                    broker_address="118.67.128.157"
                    broker_port=1883
                    client= mqtt.Client()
                    client.username_pw_set("dgo2o", "dgo2o!@")
                    client.connect(host=broker_address, port=broker_port)
                    client.publish("env/"+SH_ID+"/"+LAMP_ID, json_string)
                    client.loop(2)
                    time.sleep(7)
                
                else:
                    # print('bell - Normal State')
                    time.sleep(0.1)
                GPIO.output(20, False)
        except KeyboardInterrupt:
            GPIO.cleanup()
