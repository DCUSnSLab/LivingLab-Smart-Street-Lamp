import multiprocessing as mp
import time

from gateway.proc_environsensor import EnvironSensor
from gateway.proc_exec import procExec
from gateway.proc_testProc import testProc
from gateway.procImpl import ProcessImpl
from gateway.proc_websocket import webSocket
from gateway.proc_test1 import test_socket
from gateway.proc_test2 import test_socket2

class LampSystemManager:
    def __init__(self, manager):
        self.dataManager = manager
        self.processItems:dict[str, ProcessImpl] = dict()
        #print(type(self.dataManager))

        #create processes
        env_proc = EnvironSensor('environSensor')
        test_proc = testProc('test1')
        test2_proc = testProc('test2')
        proc_exec = procExec('exec_exam')
        socket_proc = webSocket('socket')
        sk_test_proc1 = test_socket('so1')
        sk_test_proc2 = test_socket2('so2')

        #process aggregation
        env_proc.addSubscriber(test_proc, self.dataManager)
        env_proc.addSubscriber(test2_proc, self.dataManager)

        #add process
        self.addProcess(env_proc)
        self.addProcess(test_proc)
        self.addProcess(test2_proc)
        self.addProcess(proc_exec)
        self.addProcess(socket_proc)
        self.addProcess(sk_test_proc1)
        self.addProcess(sk_test_proc2)

    def run(self):
        #process start
        for val in self.processItems.values():
            p = mp.Process(target=val.run, name=val.name)
            val.start(p)

        rcnt = len(self.processItems.keys())
        print('Process remaining [%d]'%rcnt)

        for p in self.processItems.values():
            #print('wait [%d]'%p.getPID())
            p.join()
            rcnt -= 1
            print('[%d-%s] - Finished' % (p.getPID(),p.name))
            print('Process remaining [%d]'%rcnt)


    def addProcess(self, proc:ProcessImpl):
        self.processItems[proc.name] = proc


if __name__ == '__main__':
    lc = LampSystemManager(mp.Manager())
    lc.run()