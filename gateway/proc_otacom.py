import time

import sysv_ipc

from ota.type_definitions import TYPE_STRING
from procImpl import ProcessImpl


class otaComm(ProcessImpl):
    def __init__(self):
        super().__init__('OTACommunicator')

    def doProc(self):
        try:
            mq = sysv_ipc.MessageQueue(1213, sysv_ipc.IPC_CREAT)

            while True:
                self._print('ready to start ota in 5sec')
                time.sleep(5)
                self._print('send data to ota server')
                mq.send('s', True, type=TYPE_STRING)
        except sysv_ipc.ExistentialError:
            print("ERROR: message queue creation failed")