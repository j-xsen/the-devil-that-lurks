# creates datagrams to send to server
from direct.distributed.PyDatagram import PyDatagram
from communications.codes import *


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
    dg.addUint8(game.get_vote_count())
    return dg


def dg_kick_from_game(reason):
    dg = PyDatagram()
    dg.addUint8(KICKED_FROM_GAME)
    dg.addUint8(reason)
    return dg


# Lobby
def dg_add_player(local_id, name="???"):
    """
    Tells players in lobby that a new player has joined
        uint8 - local_id
        string - name
    """
    dg = PyDatagram()
    dg.addUint8(ADD_PLAYER)
    dg.addUint8(local_id)
    dg.addString(name)
    return dg


def dg_remove_player(local_id):
    """
    Tells the players that a player has Left.
    This should only be called while the game is in the lobby as it'll delete the player's data from clients
    :param local_id: the local ID of the ex-player
    :type local_id: int
    :return: the datagram to send
    :rtype: pydatagram
    """
    dg = PyDatagram()
    dg.addUint8(REMOVE_PLAYER)
    dg.addUint8(local_id)
    return dg


def dg_update_vote_count(num):
    dg = PyDatagram()
    dg.addUint8(UPDATE_VOTE_COUNT)
    dg.addUint8(num)
    return dg


def dg_update_player_name(local_id, new_name):
    """
    Tells players that someone has updated their name
    :param local_id: the local ID of the player changing their name
    :type local_id: int
    :param new_name: the new name of the player
    :type new_name: string
    :return: the datagram to send
    :rtype: pydatagram
    """
    dg = PyDatagram()
    dg.addUint8(UPDATE_NAME)
    dg.addUint8(local_id)
    dg.addString(new_name)
    return dg


def dg_start_game(game):
    dg = PyDatagram()
    dg.addUint8(START_GAME)

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


def dg_has_died(local_id):
    """
    :param local_id: The local_id of the player who has died
    :type local_id: Uint8
    """
    dg = PyDatagram()
    dg.addUint8(HAS_DIED)
    dg.addUint8(local_id)
    return dg


def dg_you_are_killer():
    dg = PyDatagram()
    dg.addUint8(YOU_ARE_KILLER)
    return dg


def dg_kill_failed_empty_room():
    dg = PyDatagram()
    dg.addUint8(KILL_FAILED_EMPTY_ROOM)
    return dg


def dg_how_many_in_room(num):
    dg = PyDatagram()
    dg.addUint8(NUM_IN_ROOM)
    dg.addUint8(num)
    return dg
