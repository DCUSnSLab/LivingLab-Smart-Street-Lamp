import multiprocessing
import os, sys
import signal
import time
import git

def f(d, l):
    d['hello'] = 'world'
    l.append('abc')

if __name__ == '__main__':
    g= git.cmd.Git('/home/soobin/development/LivingLab-Smart-Street-Lamp')
    g.pull()
    # pid = os.fork()
    # if pid == 0:
    #     print('run child')
    #     # while True:
    #     #     time.sleep(1)
    #     #     print('aaa')
    #     os.system('python3 lampController.py')
    #
    # print('wait child - ', pid)
    # pd = os.waitpid(pid, 0)
    #
    # time.sleep(2)
    # print('kill Child - ',pid)
    # os.kill(pid, signal.SIGKILL)
    # time.sleep(5)
    # print('restart process')
    # pid = os.fork()
    # if pid == 0:
    #     print('run second child')
    #     os.system('python3 lampController.py')
    #
    # time.sleep(1)
    # print('wait process - ',pid)
    # pd = os.waitpid(pid, 0)