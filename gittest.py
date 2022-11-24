import os

import git

def f(d, l):
    d['hello'] = 'world'
    l.append('abc')

if __name__ == '__main__':
    pid = os.fork()
    if pid == 0:
        print('run child')
        # while True:
        #     time.sleep(1)
        #     print('aaa')
        os.system('git pull origin')