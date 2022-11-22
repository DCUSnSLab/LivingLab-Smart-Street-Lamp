# import multiprocessing as mp
# import time

# from gateway.proc_environsensor import EnvironSensor
# from gateway.proc_exec import procExec
# from gateway.proc_testProc import testProc
# from procImpl import ProcessImpl

# class LampSystemManager:
#     def __init__(self, manager):
#         self.dataManager = manager
#         self.processItems:dict[str, ProcessImpl] = dict()
#         #print(type(self.dataManager))

#         #create processes
#         env_proc = EnvironSensor('environSensor')
#         test_proc = testProc('test1')
#         test2_proc = testProc('test2')
#         proc_exec = procExec('exec_exam')

#         #process aggregation
#         env_proc.addSubscriber(test_proc, self.dataManager)
#         env_proc.addSubscriber(test2_proc, self.dataManager)

#         #add process
#         self.addProcess(env_proc)
#         self.addProcess(test_proc)
#         self.addProcess(test2_proc)
#         self.addProcess(proc_exec)

#     def run(self):
#         #process start
#         for val in self.processItems.values():
#             p = mp.Process(target=val.run, name=val.name)
#             val.start(p)

#         rcnt = len(self.processItems.keys())
#         print('Process remaining [%d]'%rcnt)

#         for p in self.processItems.values():
#             #print('wait [%d]'%p.getPID())
#             p.join()
#             rcnt -= 1
#             print('[%d-%s] - Finished' % (p.getPID(),p.name))
#             print('Process remaining [%d]'%rcnt)


#     def addProcess(self, proc:ProcessImpl):
#         self.processItems[proc.name] = proc


# if __name__ == '__main__':
#     lc = LampSystemManager(mp.Manager())
#     lc.run()