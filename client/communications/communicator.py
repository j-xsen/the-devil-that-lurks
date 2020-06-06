# creates datagrams to send to server
from direct.distributed.PyDatagram import PyDatagram
from communications.codes import *


# GENERAL
def dg_send_heartbeat(pid):
    dg = PyDatagram()
    dg.addUint8(HEARTBEAT)
    dg.addUint16(pid)
    return dg


def dg_goodbye(pid):
    dg = PyDatagram()
    dg.addUint8(GOODBYE)
    dg.addUint16(pid)
    return dg


# MAIN MENU
def dg_request_game(pid):
    dg = PyDatagram()
    dg.addUint8(REQUEST_GAME)
    dg.addUint16(pid)
    return dg


# LOBBY
def dg_vote_to_start(pid):
    dg = PyDatagram()
    dg.addUint8(VOTE_TO_START)
    dg.addUint16(pid)
    return dg


def dg_leave_lobby(pid):
    dg = PyDatagram()
    dg.addUint8(LEAVE_LOBBY)
    dg.addUint16(pid)
    return dg


# GAME
def dg_set_room(pid, room):
    dg = PyDatagram()
    dg.addUint8(SET_ROOM)
    dg.addUint16(pid)
    dg.addUint8(room)
    return dg


def dg_set_kill(pid, kill):
    dg = PyDatagram()
    dg.addUint8(SET_KILL)
    dg.addUint16(pid)
    dg.addBool(kill)
    return dg
