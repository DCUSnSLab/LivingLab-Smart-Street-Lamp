import multiprocessing as mp
import sys
import time
from importlib import reload

import proc_testProc
from proc_otacom import otaComm
from proc_environsensor import EnvironSensor
from proc_exec import procExec
from proc_testProc import testProc
from proc_testPub import testPublisher
from procImpl import ProcessImpl


class LampSystemManager(ProcessImpl):
    def __init__(self, manager):
        super().__init__('LampManager')
        self.dataManager = manager
        self.processItems:dict[str, ProcessImpl] = dict()
        #print(type(self.dataManager))

        self.constructProcess()

    def constructProcess(self):
        # create processes
        otacom = otaComm()
        pub_proc = testPublisher('testPublisher')
        test_proc = testProc('test1')
        test2_proc = testProc('test2')

        # process aggregation
        pub_proc.addSubscriber(test_proc, self.dataManager)
        pub_proc.addSubscriber(test2_proc, self.dataManager)
        print(pub_proc.msgQueueList)

        # add process
        self.addProcess(otacom)
        self.addProcess(pub_proc)
        self.addProcess(test_proc)
        self.addProcess(test2_proc)

    def doProc(self):
        self.__startChildProcess()

        loop_f = True
        while loop_f:
            try:
                time.sleep(60)
            except KeyboardInterrupt:
                print('?????')
                loop_f = False
            self._print('checking Process alive')
            self.printProcessStatus()
            self.__startChildProcess()
            self._print('Process checking finished')

        # for p in self.processItems.values():
        #     #print('wait [%d]'%p.getPID())
        #     p.join()
        #     rcnt -= 1
        #     print('[%d-%s] - Finished' % (p.getPID(),p.name))
        #     print('Process remaining [%d]'%rcnt)

    def __startChildProcess(self):
        # process start
        self._print('Starting Child Processes')
        for val in self.processItems.values():
            if val.is_alive() is False:
                p = mp.Process(target=val.run, name=val.name)
                val.start(p)

    def __restartAllChildProcesses(self):
        #delete all process list
        self.terminateAllProcess()
        time.sleep(1)
        self.__startChildProcess()

    def terminateProcessByName(self, name):
        if name in self.processItems:
            sp = self.processItems[name]
            sp.terminate()
            self._print('%15s(%5d) has been terminated'%(name, sp.getPID()))
        else:
            self._print('there is no Process by [%s]'%name)

    def terminateAllProcess(self):
        for val in self.processItems.values():
            val.terminate()
            self._print('%15s(%5d) has been terminated' % (val.name, val.getPID()))

    def printProcessStatus(self):
        for key, val in self.processItems.items():
            self._print("[key : %15s] [pid : %5d] [status : %5s]"%(key, val.getPID(), val.is_alive()))

    def addProcess(self, proc:ProcessImpl):
        self.processItems[proc.name] = proc

    def getProcess(self):
        return self.processItems

if __name__ == '__main__':
    lc = LampSystemManager(mp.Manager())
    lc.run()