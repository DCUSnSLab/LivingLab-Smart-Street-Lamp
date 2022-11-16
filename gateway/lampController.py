import multiprocessing as mp

from procImpl import ProcessImpl


class LampSystemManager:
    def __init__(self):
        pass

    def run(self):
        p = mp.Process(target=ProcessImpl, name='subProc', args=("bob",))
        p.start()


if __name__ == '__main__':
    lc = LampSystemManager()
    lc.run()