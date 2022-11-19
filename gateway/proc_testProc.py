from gateway.procImpl import ProcessImpl


class testProc(ProcessImpl):
    def __init__(self, name):
        super().__init__(name)

    def doProc(self):
        while(True):
            try:
                data = self.aggQueue.get()
                self._print(data)
            except Exception as e:
                self._print(e)