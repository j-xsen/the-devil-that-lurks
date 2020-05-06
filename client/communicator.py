# creates datagrams to send to server
from direct.distributed.PyDatagram import PyDatagram
from codes import *


def dg_request_game(pid):
    dg = PyDatagram()
    dg.addUint8(REQUEST_GAME)
    dg.addUint16(pid)
    return dg


def dg_vote_to_start(pid):
    dg = PyDatagram()
    dg.addUint8(VOTE_TO_START)
    dg.addUint16(pid)
    return dg
