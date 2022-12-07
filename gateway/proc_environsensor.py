import time
import os
import fcntl
import sysv_ipc
import numpy as np
import struct

from gateway.procImpl import ProcessImpl
from ota.type_definitions import *

class EnvironSensor(ProcessImpl):
    def __init__(self, name):
        super().__init__(name)

    def map_(self,x,input_min,input_max,output_min,output_max):
        a = (x-input_min)*(output_max-output_min)/(input_max-input_min)+output_min
        return a

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

                try:
                    mq = sysv_ipc.MessageQueue(1234, sysv_ipc.IPC_CREAT, 0o666)
                    # numpy array transmission
                    print("tranmission")
                    mq.send(msg_npy.tobytes(order='C'), True, type=TYPE_NUMPY)
                    print(f"numpy array sent: {msg_npy}")
                except sysv_ipc.ExistentialError:
                    print("ERROR: message queue creation failed")
                time.sleep(10)
        except KeyboardInterrupt:
            os.close(fd)