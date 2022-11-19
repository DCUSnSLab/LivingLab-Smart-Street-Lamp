import time

from gateway.procImpl import ProcessImpl


class EnvironSensor(ProcessImpl):
    def __init__(self, name):
        super().__init__(name)

    def doProc(self):
        a = 0
        while a<5:
            for q in self.msgQueueList:
                q.put([a,'data'])
            a+=1
            time.sleep(0.5)