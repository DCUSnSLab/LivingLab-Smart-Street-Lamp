import multiprocessing
import os, sys


def f(d, l):
    d['hello'] = 'world'
    l.append('abc')

if __name__ == '__main__':
    pid = os.fork()
    if pid == 0:
        print('run child')
        os.execl('test1', 'test1', *sys.argv)
    print('wait child - ',pid)
    pd = os.wait()
    print('test ok',pd)