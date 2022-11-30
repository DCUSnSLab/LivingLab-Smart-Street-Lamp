import os, sys
import signal
import time
import psutil

from multiprocessing import active_children

import sysv_ipc
import numpy as np
import struct

def startLamp():
    pid = os.fork()
    if pid == 0:
        print('run child')
        # while True:
        #     time.sleep(1)
        #     print('aaa')
        os.system('python3 lampController.py')
    return pid

def startGitPull():
    pid = os.fork()
    if pid == 0:
        print('Git Pulling from server')
        os.system('sh gitpull.sh')

def killLamp(pid):
    print('KILL LAMP-',pid)
    proc = psutil.Process(pid)
    children = proc.children(recursive=True)
    children.append(proc)
    for p in children:
        p.kill()
    os.kill(pid, signal.SIGKILL)
    time.sleep(1)

if __name__ == '__main__':
    pid = os.fork()
    print('start child node ', pid)
    if pid == 0:
        print('run child')
        # while True:
        #     time.sleep(1)
        #     print('aaa')
        os.system('python3 lampController.py')
    #
    # print('wait child - ', pid)
    # pd = os.waitpid(pid, 0)
    #

    time.sleep(5)
    print('kill Child - ',pid)
    killLamp(pid)
    time.sleep(10)
    os.waitpid(pid, 0)
