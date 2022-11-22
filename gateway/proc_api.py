import requests
import xml.etree.ElementTree as ET
import datetime as dt
import RPi.GPIO as GPIO
import time

from gateway.procImpl import ProcessImpl


class SunAPI(ProcessImpl):
    def __init__(self, name):
        super().__init__(name)

    def doProc(self):
        led = 16
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(led, GPIO.OUT)

        try:
            while 1:
                x = dt.datetime.now()

                url = 'http://apis.data.go.kr/B090041/openapi/service/RiseSetInfoService/getAreaRiseSetInfo'
                params ={'serviceKey' : 'FSiJ0gZ5rLtvA6IM8LeEFCA2CCiR/KlhEBHq0+RtS0YSG6wStGx5dfvyAfiVc0WzRWtdSwZmEtwpULyA0kDvig==', 'locdate' : x.strftime("%Y%m%d"), 'location' : '대구' }

                response = requests.get(url, params=params)
                list = ['nautm', 'naute']

                file1 = response.content.decode('utf-8')
                tree = ET.fromstring(file1)
                tree = tree.findall('body/items/item')
                for item in tree:
                    for i in item:
                        if i.tag in list:
                            print(i.tag, i.text)
                        if(i.tag == 'nautm'):
                            # print(i.tag, i.text)
                            sunrise = i.text
                        elif(i.tag == 'naute'):
                            sunset = i.text
                
                timenow = x.strftime("%H%M")
                if timenow >= sunset or timenow <= sunrise:
                    print("on")
                    GPIO.output(led, GPIO.HIGH)
                else:
                    print("off")
                    GPIO.output(led, GPIO.LOW)
                time.sleep(5)
        except KeyboardInterrupt:
            GPIO.cleanup()