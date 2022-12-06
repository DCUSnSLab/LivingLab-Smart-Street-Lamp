import os, sys
import signal
import time

import psutil

from type_definitions import *
import numpy as np
import struct
import sysv_ipc

def startLamp():
    pid = os.fork()
    if pid == 0:
        print('run child')
        # while True:
        #     time.sleep(1)
        #     print('aaa')
        os.system('python3 ./gateway/lampController.py')
    return pid

def startGitPull():
    pid = os.fork()
    if pid == 0:
        print('Git Pulling from server')
        os.system('sh ./gateway/ota/gitpull.sh')
    print('wait gitpull')
    os.waitpid(pid, 0)

def killLamp(pid):
    print('KILL LAMP-',pid)
    proc = psutil.Process(pid)
    #proc.terminate()
    children = proc.children(recursive=True)
    children.append(proc)
    for p in children:
        print(p)
        #p.kill()
        os.system("kill -9 "+str(p.pid))
    #os.kill(pid, signal.SIGKILL)
    os.system("kill -9 "+str(pid))
    proc.wait(timeout=5)
    print('all process killed')
    time.sleep(1)

def sighandle(signum, frame):
    print('signal execute!!!!!')
    exit()

if __name__ == '__main__':
    BUFF_SIZE = 16
    SIZEOF_FLOAT = 8
    pid = 0
    try:
        signal.signal(signal.SIGINT, sighandle)
        pid = startLamp()
        print('start child node ',pid)
        time.sleep(2)
        mq = sysv_ipc.MessageQueue(1213, sysv_ipc.IPC_CREAT)

        while True:
            print('wait for OTA reqeust...')
            message, mtype = mq.receive()
            print("*** New message received ***")
            print(f"Raw message: {message}", mtype)
            if mtype == TYPE_STRING:
                str_message = message.decode()
                print('1111', str_message)
                if str_message == "s":
                    killLamp(pid)
                    startGitPull()
                    pid = startLamp()

    except sysv_ipc.ExistentialError:
        print("ERROR: message queue creation failed")