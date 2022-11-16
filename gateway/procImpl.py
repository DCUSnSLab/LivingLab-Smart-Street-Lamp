import multiprocessing as mp


class ProcessImpl():
    def __init__(self, name):
        self.pid = mp.current_process().pid
        self.name = mp.current_process().name
        self.run()

    def run(self):
        print('run target')