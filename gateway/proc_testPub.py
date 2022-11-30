import time

from procImpl import ProcessImpl


class testPublisher(ProcessImpl):
    def __init__(self, name):
        super().__init__(name)

    def doProc(self):
        a = 0
        while True:
            self._SendtoAll(a)
            a+=1
            time.sleep(0.5)