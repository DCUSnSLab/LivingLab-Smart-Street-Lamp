import os
import sys

from gateway.procImpl import ProcessImpl


class procExec(ProcessImpl):
    def __init__(self, name):
        super().__init__(name)

    def doProc(self):
        self._print('run Child')
        os.execl('test1', 'test1', *sys.argv)
        self._print('execl Child')