# creates datagrams to send to server
from direct.distributed.PyDatagram import PyDatagram
from codes import *


def dg_deliver_game():
    dg = PyDatagram()
    dg.addUint8(DELIVER_GAME)
    return dg
