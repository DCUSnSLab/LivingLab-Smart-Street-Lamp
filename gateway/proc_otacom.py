import asyncio
import json
import time

import sysv_ipc
import websockets

from ota.type_definitions import TYPE_STRING
from procImpl import ProcessImpl


class otaComm(ProcessImpl):
    def __init__(self):
        super().__init__('OTACommunicator')

    async def accept(self, websocket, path):
        print("accept_func")
        # print('accepted', websocket.origin, websocket.id)
        mq = sysv_ipc.MessageQueue(1213, sysv_ipc.IPC_CREAT)
        while True:
            print('accepted')
            data = await websocket.recv()  # 클라이언트로부터 메시지를 대기한다.
            recvdata = json.loads(data)
            recvMsg = str(recvdata['message'])
            print(recvMsg)
            try:
                mq.send(recvMsg, True, type=TYPE_STRING)
                print(f"string sent: {recvMsg}")
            except sysv_ipc.ExistentialError:
                print("ERROR: message queue creation failed")
            # recvdata = json.loads(data)
            # recvMsg = int(recvdata['message'])

            # if you receive '0' data from client once, add client socket into Advertiser client list
            # if recvMsg == 0:  # advertise mode ready to client
            #     print("recv Messages", recvMsg)
            # else:
            #     print("Wrong Messages", data)

    def doProc(self):
        # await websockets.serve(self.accept(), "localhost", 5000)
        start_server = websockets.serve(self.accept, "localhost", 5000)
        # 비동기로 서버를 대기한다.
        asyncio.get_event_loop().run_until_complete(start_server)
        asyncio.get_event_loop().run_forever()
