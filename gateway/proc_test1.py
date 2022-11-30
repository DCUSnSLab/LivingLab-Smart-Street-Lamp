import sysv_ipc
import numpy
import struct

from gateway.procImpl import ProcessImpl
from type_definitions import *

BUFF_SIZE = 16

class test_socket(ProcessImpl):
    def __init__(self, name):
        super().__init__(name)

    def doProc(self):
        try:
            mq = sysv_ipc.MessageQueue(1234, sysv_ipc.IPC_CREAT)
            while(True):
                message, mtype = mq.receive()
                print("*** [proc_test1:1234] New message received ***")
                print(f"Raw message: {message}")
                if mtype == TYPE_STRING:
                    str_message = message.decode()
                    print(f"Interpret as string: {str_message}")
                if str_message.find('test') != -1:
                    print(">>proc_test1 control<<")
        except sysv_ipc.ExistentialError:
            print("ERROR : message queue creation failed")
