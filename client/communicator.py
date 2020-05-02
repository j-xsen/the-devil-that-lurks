# creates datagrams to send to server
from direct.distributed import PyDatagram

REQUEST_GAME = 1

def request_game:
    dg = PyDatagram()
    dg.addUint8(REQUEST_GAME)
    return dg
