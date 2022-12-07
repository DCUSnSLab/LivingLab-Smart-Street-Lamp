import os
import sys

from gateway.procImpl import ProcessImpl


class matrix(ProcessImpl):
    def __init__(self, name):
        super().__init__(name)

    def doProc(self):
        self._print('run Child')
        # os.execl('/home/pi/LivingLab-Smart-Street-Lamp/gateway/text-example','/home/pi/LivingLab-Smart-Street-Lamp/gateway/text-example', "--led-cols=64", "-f", "/home/pi/LivingLab-Smart-Street-Lamp/gateway/rpi-rgb-led-matrix/fonts//Galmuri9.bdf", "--led-slowdown-gpio=3")
        os.system("sudo /home/pi/LivingLab-Smart-Street-Lamp/gateway/rpi-rgb-led-matrix/examples-api-use/text-example --led-cols=64 -f /home/pi/LivingLab-Smart-Street-Lamp/gateway/rpi-rgb-led-matrix/fonts//Galmuri9.bdf --led-slowdown-gpio=3")
        # sudo ./text-example --led-cols=64 -f ../fonts//Galmuri9.bdf --led-slowdown-gpio=3
        self._print('execl Child')