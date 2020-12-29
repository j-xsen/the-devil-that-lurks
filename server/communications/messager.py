from communications.codes import *
from communications.datagrams import dg_deliver_pid, dg_deliver_game, dg_kick_from_game, dg_kill_connection
from direct.directnotify.DirectNotifyGlobal import directNotify
from direct.task import Task
from config import *
from objects.game import Game

# random
from direct.showbase.RandomNumGen import RandomNumGen
import time

# network
from panda3d.core import QueuedConnectionManager
from panda3d.core import QueuedConnectionListener
from panda3d.core import QueuedConnectionReader
from panda3d.core import ConnectionWriter
from panda3d.core import PointerToConnection, NetAddress, NetDatagram
from direct.distributed.PyDatagramIterator import PyDatagramIterator


"""

This class receives and decodes messages

"""


class Messager:

    # notify
    notify = directNotify.newCategory("msgr")

    # network
    cManager = QueuedConnectionManager()
    cListener = QueuedConnectionListener(cManager, 0)
    cReader = QueuedConnectionReader(cManager, 0)
    cWriter = ConnectionWriter(cManager, 0)

    def __init__(self):
        # dicts
        self.active_connections = {}
        self.games = {}

        port_address = SERVER_PORT
        backlog = 1000
        tcpSocket = self.cManager.openTCPServerRendezvous(port_address, backlog)
        self.cListener.addConnection(tcpSocket)

        return

    def check_for_new_players(self, taskdata):
        """
        Called repeatedly to check if there's any new connections
        If there are, add them to self.active_connections
        """
        if self.cListener.newConnectionAvailable():
            rendezvous = PointerToConnection()
            net_address = NetAddress()
            new_connection = PointerToConnection()

            if self.cListener.getNewConnection(rendezvous, net_address, new_connection):
                self.notify.info("New connection")
                new_connection = new_connection.p()

                pid = self.create_pid()

                self.active_connections[pid] = {"connection": new_connection,
                                                "gid": None,
                                                "heartbeat": True}

                self.cReader.add_connection(new_connection)

                self.cWriter.send(dg_deliver_pid(pid), new_connection)
        return Task.cont

    def check_for_message(self, taskdata):
        """
        Called repeatedly to check if there's any new messages
        """
        if self.cReader.dataAvailable():
            dg = NetDatagram()
            if self.cReader.getData(dg):
                iterator = PyDatagramIterator(dg)
                connection = dg.getConnection()

                try:
                    msg_id = iterator.getUint8()
                except AssertionError:
                    self.notify.warning("No message ID")
                    return Task.cont

                # check if real msg_id
                if msg_id in self.mapping:
                    self.mapping[msg_id](self, iterator)
                else:
                    self.notify.warning("Invalid msg_id: {}".format(msg_id))
        return Task.cont

    def check_heartbeats(self, task):
        self.notify.debug("Checking heartbeats")
        for pid in self.active_connections:
            connection = self.active_connections[pid]
            if connection["heartbeat"]:
                connection["heartbeat"] = False
            else:
                self.notify.debug(f"Player {connection['pid']} has no heartbeat!")
                self.remove_player(connection["pid"], NO_HEART)
        return task.again

    """
    # Utility
    """
    def create_game(self, pid):
        """
        Creates a game for the PID given
        :param pid: PID of player wanting to join a game
        :type pid: int
        :return: if successful
        :rtype: bool
        """
        gid = RandomNumGen(int(round(time.time() * 1000))).randint(0, 65535)

        self.notify.debug("create game: {}".format(gid))

        # create game
        game = Game(gid, self)
        self.games[gid] = game

        self.add_player_to_game(pid, game.gid)

        return True

    def delete_game(self, gid):
        """
        Deletes the game of the GID given
        :param gid: the game ID
        :type gid: int
        :return: if successful
        :rtype: bool
        """
        self.notify.debug("delete game: {}".format(gid))

        # remove gid from players
        for p in self.games[gid].players:
            if not p.ai:
                self.active_connections[p.pid]["gid"] = None

        del self.games[gid]

        return True

    def add_player_to_game(self, pid, gid):
        """
        Adds a player to a game
        :param pid: the player ID of the player joining the game
        :type pid: int
        :param gid: the game ID of the game the player wants to join
        :type gid: int
        :return: if successful
        :rtype: bool
        """
        self.notify.debug("adding player {} to game {}".format(pid, gid))
        self.active_connections[pid]["gid"] = gid
        self.send_message(pid, dg_deliver_game(self.games[gid]))
        self.games[gid].add_player(pid)
        return True

    def remove_player_from_game(self, pid, reason):
        """
        Removes a player from a game
        :param pid: the player ID of the player leaving the game
        :type pid: int
        :param reason: the reason they're being removed from the game (see 3- codes)
        :type reason: int
        """
        self.notify.debug("removing player {}".format(pid))
        self.games[self.active_connections[pid]["gid"]].remove_player(pid=pid)
        self.active_connections[pid]["gid"] = None
        self.cWriter.send(dg_kick_from_game(reason), self.active_connections[pid]["connection"])

    def remove_player(self, pid, reason):
        """
        remove a player from The System
        :param pid: the player ID
        :type pid: int
        :return: if successful
        :rtype: bool
        """
        self.notify.debug("remove_player PID: {}".format(pid))

        if pid not in self.active_connections:
            self.notify.warning(f"Requested to remove non-existent player PID {pid}")
            return False

        if self.active_connections[pid]["gid"]:
            self.remove_player_from_game(pid, reason)

        self.cWriter.send(dg_kill_connection(), self.active_connections[pid]["connection"])
        del self.active_connections[pid]

        return True

    def send_message(self, pid, dg):
        """
        Sends a message to a client
        :param pid: the PID of the player you want to message
        :type pid: int
        :param dg: the datagram you want to send
        :type dg: PyDatagram
        :return: if successful
        :rtype: bool
        """
        if not pid:
            self.notify.warning("Requested to send message with no PID")
            return False
        self.cWriter.send(dg, self.active_connections[pid]["connection"])

    def create_pid(self):
        """
        Create a new PID
        :return: a new, unique PID
        :rtype: int
        """
        pid = None
        while not pid:
            temp_pid = RandomNumGen(int(round(time.time() * 1000))).randint(0, 65535)
            if temp_pid not in self.active_connections:
                pid = temp_pid
        return pid

    """
    # Message Codes
    """

    def request_game(self, iterator):
        """
        Called when someone requests a game
            uint16 - pid: the client's player ID
        :return: if successful
        :rtype: bool
        """
        try:
            pid = iterator.getUint16()
        except AssertionError:
            self.notify.warning("Received invalid REQUEST_GAME")
            return False

        if not self.active_connections[pid]["gid"]:
            game = None

            for g in self.games:
                # make sure game meets our qualifications
                if self.games[g].open and not self.games[g].started:
                    game = self.games[g]
                    break

            if game:
                self.add_player_to_game(pid, game.get_gid())
            else:
                self.notify.debug("No available games, make one")
                self.create_game(pid)
        else:
            self.notify.warning("{} requested game while already in a game".format(pid))
            return False

        return True

    #TODO add bool
    def vote_to_start(self, iterator):
        """
        Called when a player votes to start the game
            uint16 - pid: the client's player ID
        :return: if successful
        :rtype: bool
        """
        try:
            pid = iterator.getUint16()
        except AssertionError:
            self.notify.warning("Received invalid VOTE_TO_START")
            return False

        game = self.games[self.active_connections[pid]["gid"]]

        if not game:
            self.notify.warning("No game for {}".format(pid))
            return False

        game.vote_to_start(pid)
        return True

    def leave_lobby(self, iterator):
        """
        Called when people tell the server they're leaving the lobby
            uint16 - pid: the player ID
        :return: if successful
        :rtype: bool
        """
        try:
            pid = iterator.getUint16()
        except AssertionError:
            self.notify.warning("Received invalid LEAVE_LOBBY")
            return False

        return self.remove_player_from_game(pid, LEFT_GAME)

    def set_room(self, iterator):
        """
        Called when a player tells the server what room they want to be in
            uint16 - pid: the player ID
            uint8 - room: the room the player wants to be in
        :return: if successful
        :rtype: bool
        """
        try:
            pid = iterator.getUint16()
            room = iterator.getUint8()
        except AssertionError:
            self.notify.warning("Received invalid SET_ROOM")
            return False

        game = self.games[self.active_connections[pid]["gid"]]

        if not game:
            self.notify.warning("{} attempted to set room while not in a game".format(pid))
            return False

        game.set_player_room(pid, room)
        return True

    def set_kill(self, iterator):
        """
        Called when a player (who is a killer) tells the server if they want to kill
            uint16 - pid: the player ID
            bool - choice: the player's choice of killing
        :return: if successful
        :rtype: bool
        """
        try:
            pid = iterator.getUint16()
            choice = iterator.getBool()
        except AssertionError:
            self.notify.warning("Received invalid SET_KILL")
            return False

        game = self.games[self.active_connections[pid]["gid"]]

        if not game:
            self.notify.warning("{} attempted to set kill while not in a game".format(pid))
            return False

        game.set_kill_choice(pid, choice)
        return True

    def heartbeat(self, iterator):
        """
        Heartbeat to keep client connected
            uint16 - pid: the player ID
        :return: if successful
        :rtype: bool
        """
        try:
            pid = iterator.getUint16()
        except AssertionError:
            self.notify.warning("Received invalid HEARTBEAT")
            return False

        self.notify.debug(f"Received heartbeat from PID {pid}")
        self.active_connections[pid]["heartbeat"] = True
        return True

    def goodbye(self, iterator):
        """
        Called when the client closes the connection
            uint16 - pid: the player ID
        :return: if successful
        :rtype: bool
        """
        try:
            pid = iterator.getUint16()
        except AssertionError:
            self.notify.warning("Received invalid GOODBYE")
            return False

        return self.remove_player(pid, CLIENT_LOG_OFF)

    def update_name(self, iterator):
        """
        Called when a player says they want to change their name
        :return: if successful
        :rtype: bool
        """
        try:
            pid = iterator.getUint16()
            new_name = iterator.getString()
        except AssertionError:
            self.notify.warning("Received invalid UPDATE_NAME")
            return False

        self.games[self.active_connections[pid]["gid"]].set_name(pid, new_name)
        return True

    # Mapping
    mapping = {
        REQUEST_GAME: request_game,
        VOTE_TO_START: vote_to_start,
        LEAVE_LOBBY: leave_lobby,
        SET_ROOM: set_room,
        SET_KILL: set_kill,
        HEARTBEAT: heartbeat,
        GOODBYE: goodbye,
        UPDATE_NAME: update_name
    }
