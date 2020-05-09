# creates datagrams to send to server
from direct.distributed.PyDatagram import PyDatagram
from codes import *


# General
def dg_kill_connection():
    dg = PyDatagram()
    dg.addUint8(KILLED_CONNECTION)
    return dg


# Main menu
def dg_deliver_pid(pid):
    dg = PyDatagram()
    dg.addUint8(DELIVER_PID)
    dg.addUint16(pid)
    return dg


def dg_deliver_game(game):
    dg = PyDatagram()
    dg.addUint8(DELIVER_GAME)
    dg.addUint8(game.get_player_count())
    dg.addUint8(game.get_vote_count())
    return dg


def dg_kick_from_game(reason):
    dg = PyDatagram()
    dg.addUint8(KICKED_FROM_GAME)
    dg.addUint8(reason)
    return dg


# Lobby
def dg_update_player_count(num):
    dg = PyDatagram()
    dg.addUint8(UPDATE_PLAYER_COUNT)
    dg.addUint8(num)
    return dg


def dg_update_vote_count(num):
    dg = PyDatagram()
    dg.addUint8(UPDATE_VOTE_COUNT)
    dg.addUint8(num)
    return dg


def dg_start_game(game):
    dg = PyDatagram()
    dg.addUint8(START_GAME)

    for p in game.players:
        dg.addString(p.get_name())
        dg.addUint8(p.get_local_id())

    return dg


# Game
def dg_goto_day(game):
    dg = PyDatagram()
    dg.addUint8(GOTO_DAY)
    dg.addUint8(game.day_count)
    dg.addUint8(game.red_room)
    return dg


def dg_goto_night(game):
    dg = PyDatagram()
    dg.addUint8(GOTO_NIGHT)
    return dg


def dg_you_are_killer():
    dg = PyDatagram()
    dg.addUint8(YOU_ARE_KILLER)
    return dg


def dg_kill_failed_empty_room():
    dg = PyDatagram()
    dg.addUint8(KILL_FAILED_EMPTY_ROOM)
    return dg
