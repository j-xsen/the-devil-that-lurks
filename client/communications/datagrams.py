# creates datagrams to send to server
from direct.distributed.PyDatagram import PyDatagram
from communications.codes import *


# GENERAL
def dg_send_heartbeat(pid):
    if pid is not None:
        dg = PyDatagram()
        dg.addUint8(HEARTBEAT)
        dg.addUint16(pid)
        return dg
    else:
        print("!! TRIED TO SEND DATAGRAM WITH NO PID !!")


def dg_goodbye(pid):
    if pid is not None:
        dg = PyDatagram()
        dg.addUint8(GOODBYE)
        dg.addUint16(pid)
        return dg
    else:
        print("!! TRIED TO SEND DATAGRAM WITH NO PID !!")


# MAIN MENU
def dg_request_game(pid):
    if pid is not None:
        dg = PyDatagram()
        dg.addUint8(REQUEST_GAME)
        dg.addUint16(pid)
        return dg
    else:
        print("!! TRIED TO SEND DATAGRAM WITH NO PID !!")


# LOBBY
def dg_vote_to_start(pid):
    if pid is not None:
        dg = PyDatagram()
        dg.addUint8(VOTE_TO_START)
        dg.addUint16(pid)
        return dg
    else:
        print("!! TRIED TO SEND DATAGRAM WITH NO PID !!")


def dg_leave_lobby(pid):
    if pid is not None:
        dg = PyDatagram()
        dg.addUint8(LEAVE_LOBBY)
        dg.addUint16(pid)
        return dg
    else:
        print("!! TRIED TO SEND DATAGRAM WITH NO PID !!")


def dg_update_name(pid, name):
    """
    Call when you want to update your name
    @param pid: player ID
    @type pid: int
    @param name: new name
    @type name: string
    @return: the datagram you need to send
    @rtype: datagram
    """
    if pid is not None:
        dg = PyDatagram()
        dg.addUint8(UPDATE_NAME)
        dg.addUint16(pid)
        dg.addString(name)
        return dg
    else:
        print("!! TRIED TO SEND DATAGRAM WITH NO PID !!")


# GAME
def dg_set_room(pid, room):
    if pid is not None:
        dg = PyDatagram()
        dg.addUint8(SET_ROOM)
        dg.addUint16(pid)
        dg.addUint8(room)
        return dg
    else:
        print("!! TRIED TO SEND DATAGRAM WITH NO PID !!")


def dg_set_kill(pid, kill):
    if pid is not None:
        dg = PyDatagram()
        dg.addUint8(SET_KILL)
        dg.addUint16(pid)
        dg.addBool(kill)
        return dg
    else:
        print("!! TRIED TO SEND DATAGRAM WITH NO PID !!")
