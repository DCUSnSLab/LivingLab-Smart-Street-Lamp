import multiprocessing as mp
import multiprocessing.context
import multiprocessing.managers
from abc import *
from queue import Queue


class ProcessImpl(metaclass=ABCMeta):
    def __init__(self, name):
        # self.msgQueueList:list[Queue] = list()
        self.aggQueue:Queue = None
        self.name = name
        self.process = None
        #self.run()

    def addSubscriber(self, toProc, manager):
        tqueue = manager.Queue()
        # self.msgQueueList.append(tqueue)
        toProc.__addPublisher(tqueue)

    def __addPublisher(self, queue:Queue):
        self.aggQueue = queue

    def start(self, proc:multiprocessing.context.Process):
        self.process = proc
        self.process.start()
        self._print('start Process')

    def is_alive(self):
        return self.process.is_alive()

    def getPID(self):
        return self.process.pid

    def join(self):
        self.process.join()

    def terminate(self):
        self.process.terminate()

    def run(self):
        self.doProc()
        self.__done()
        # a = 0
        # while a < 5:
        #
        #     #print('run target')
        #     self.msgQueue.put([1, 2, 3])
        #     time.sleep(1)
        #     a+=1

    @abstractmethod
    def doProc(self):
        pass

    def __done(self):
        self._print('Finished Process')

    def _print(self, data):
        print('[%d-%s] - %s'%(self.getPID(), self.name, data))