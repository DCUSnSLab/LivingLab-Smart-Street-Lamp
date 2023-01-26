import time
import os
import fcntl
import sysv_ipc
import numpy as np
import struct
import paho.mqtt.client as mqtt
import json
import datetime as dt

from gateway.procImpl import ProcessImpl
from ota.type_definitions import *

class EnvironSensor(ProcessImpl):
    def __init__(self, name):
        super().__init__(name)

    def map_(self,x,input_min,input_max,output_min,output_max):
        a = (x-input_min)*(output_max-output_min)/(input_max-input_min)+output_min
        return a

    #MQTT 클라이언트가 MQTT 서버에 정상 접속된 후 CONNACK 응답을 받음.
    def on_connect_(self, client, userdata, flags, rc):
        print("Connected with result code "+str(rc))
        # Subscribing in on_connect() means that if we lose the connection and
        # reconnect then subscriptions will be renewed.
        #client.subscribe("$SYS/#")
        client.subscribe("mqtt/myiot/#")

    # The callback for when a PUBLISH message is received from the server.
    def on_message_(self, client, userdata, msg):
        print(msg.topic+" "+str(msg.payload))

    def doProc(self):
        I2C_SLAVE = 0x703
        sensor = 0x28

        fd = os.open('/dev/i2c-1',os.O_RDWR)
        if fd < 0 :
            print("Failed to open the i2c bus\n")
        io = fcntl.ioctl(fd,I2C_SLAVE,sensor)
        if io < 0 :
            print("Failed to acquire bus access/or talk to salve\n")

        BUFF_SIZE = 24
        try:
            while True:
                data = os.read(fd,32)
                # for i in range(0, 32):
                #     print(int(data[i]), end=" ")
                # print()

                co2_3 = int(data[3])
                co2_4 = int(data[4])
                humd = int(self.map_(256 * data[7] + data[8], 50, 990, 5, 99))
                temp = int(self.map_(256*data[9]+data[10], 100, 1350, -40, 85))
                fine = 256*int(data[15])+int(data[16])
                ultra = 256*int(data[13])+int(data[14])
                res = [co2_3, co2_4, humd, temp, fine, ultra]
                msg_npy = np.array(res)
                
                x = dt.datetime.now()

                json_object = {
                    "sh_id": "S001",
                    "lamp_id": "L001",
                    "datetime": x.strftime("%Y%m%d%H%M%S"),
                    "temp": temp,
                    "hum": humd,
                    "illum": "400",
                    # "info": {
                    #     "event": "4",
                    # },
                }
                json_string = json.dumps(json_object)

                client = mqtt.Client("env/S001/L001")
                # client.username_pw_set("dgo2o", "dgo2o!@")
                client.connect("118.67.128.157", 1883)
                client.publish("env/S001/L001", json_string)  # topic, message
                print("published")
                client.on_connect = self.on_connect_
                client.on_message = self.on_message_
                client.loop(2)

                try:
                    mq = sysv_ipc.MessageQueue(1234, sysv_ipc.IPC_CREAT, 0o666)
                    # numpy array transmission
                    # print("tranmission")
                    mq.send(msg_npy.tobytes(order='C'), True, type=TYPE_NUMPY)
                    # print(f"numpy array sent: {msg_npy}")
                except sysv_ipc.ExistentialError:
                    print("ERROR: message queue creation failed")
                time.sleep(10)
        except KeyboardInterrupt:
            os.close(fd)
