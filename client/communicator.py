# creates datagrams to send to server
from direct.distributed.PyDatagram import PyDatagram
from codes import *


def dg_request_game():
    dg = PyDatagram()
    dg.addUint8(REQUEST_GAME)
    return dg
