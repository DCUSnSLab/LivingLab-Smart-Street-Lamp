import time
import os
import fcntl
import sysv_ipc
import numpy as np
import struct

import paho.mqtt.client as mqtt
import paho.mqtt.publish as publish

import json
import datetime as dt

from ota.type_definitions import *

# #MQTT 클라이언트가 MQTT 서버에 정상 접속된 후 CONNACK 응답을 받음.
# def on_connect_(self, client, userdata, flags, rc):
#     print("Connected with result code "+str(rc))
#     # Subscribing in on_connect() means that if we lose the connection and
#     # reconnect then subscriptions will be renewed.
#     # client.subscribe("mqtt/myiot/#")

# # # The callback for when a PUBLISH message is received from the server.
# def on_message_(self, client, userdata, msg):
#     print(msg.topic+" "+str(msg.payload))

# json_object = {
#     "sh_id": SH_ID,
#     "lamp_id": LAMP_ID,
#     "datetime": x.strftime("%Y%m%d%H%M%S"),
# }
# json_string = json.dumps(json_object)

# client = mqtt.Client("env/"+SH_ID+"/"+LAMP_ID)
# client.username_pw_set("dgo2o", "dgo2o!@")
# client.connect("118.67.128.157", 1883)
# client.publish("env/"+SH_ID+"/"+LAMP_ID, json_string)  # topic, message
# client.on_connect = self.on_connect_
# client.on_message = self.on_message_
# print("published")
# client.loop(2)

while True:
  broker_address="localhost"
  broker_port=1883
  client= mqtt.Client()
  client.username_pw_set("user", "1234")
  client.connect(host=broker_address, port=broker_port)

  x = dt.datetime.now()
  
  json_object = {
      "sh_id": SH_ID,
      "lamp_id": LAMP_ID,
      "datetime": x.strftime("%Y%m%d%H%M%S"),
  }
  json_string = json.dumps(json_object)

  client.publish("env/"+SH_ID+"/"+LAMP_ID, json_string)
  client.loop(2)
  time.sleep(10)