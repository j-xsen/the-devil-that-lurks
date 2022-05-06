from communications.codes import *
from communications.datagrams import dg_deliver_pid, dg_deliver_game, dg_kick_from_game, dg_kill_connection
from objects.notifier import Notifier
from direct.task import Task
from config import *
from objects.game import Game
from objects.connection_holder import ConnectionHolder

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

# debug
from debug.debug_ui import DebugUI


"""

This class receives and decodes messages

"""


class Messager(Notifier):

    # network
    cManager = QueuedConnectionManager()
    cListener = QueuedConnectionListener(cManager, 0)
    cReader = QueuedConnectionReader(cManager, 0)
    cWriter = ConnectionWriter(cManager, 0)

    def __init__(self):
        Notifier.__init__(self, "msgr")

        # dicts
        self.active_connections = {}
        self.games = {}

        port_address = SERVER_PORT
        backlog = 1000
        tcp_socket = self.cManager.openTCPServerRendezvous(port_address, backlog)
        self.cListener.addConnection(tcp_socket)

        self.debug_ui = DebugUI(self)

        self.notify.info("[__init__] Created Messager")

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
                self.notify.debug("[check_for_new_players] New connection")
                new_connection = new_connection.p()

                pid = self.create_pid()

                new_connection_holder = ConnectionHolder(new_connection, pid)
                self.active_connections[pid] = new_connection_holder

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
                    self.notify.warning("[check_for_message] No message ID")
                    return Task.cont

                # check if real msg_id
                if msg_id in self.mapping:
                    self.mapping[msg_id](self, iterator)
                else:
                    self.notify.warning("[check_for_message] Invalid msg_id: {}".format(msg_id))
        return Task.cont

    def check_heartbeats(self, task):
        for pid in list(self.active_connections):
            connection_holder = self.active_connections[pid]
            if connection_holder.heartbeat:
                connection_holder.heartbeat = False
            else:
                self.notify.debug(f"[check_heartbeats] Player {connection_holder.pid} has no heartbeat!")
                self.remove_player(connection_holder.pid, NO_HEART)
        return task.again

    """
    # Utility
    """
    def create_game(self, pid):
        """
        Creates a game for the PID given
        @param pid: PID of player wanting to join a game
        @type pid: int
        @return: if successful
        @rtype: bool
        """
        gid = RandomNumGen(int(round(time.time() * 1000))).randint(0, 65535)

        self.notify.debug(f"[create_game] Create game {gid} for player {pid}")

        # create game
        game = Game(gid, self)
        self.games[gid] = game

        self.add_player_to_game(pid, game.gid)

        return True

    def delete_game(self, gid):
        """
        Deletes the game of the GID given
        @param gid: the game ID
        @type gid: int
        @return: if successful
        @rtype: bool
        """
        self.notify.debug(f"[delete_game] Deleting game {gid}")

        # remove gid from players
        for p in self.games[gid].players:
            if not p.ai:
                self.active_connections[p.pid].gid = None

        del self.games[gid]

        return True

    def add_player_to_game(self, pid, gid):
        """
        Adds a player to a game
        @param pid: the player ID of the player joining the game
        @type pid: int
        @param gid: the game ID of the game the player wants to join
        @type gid: int
        @return: if successful
        @rtype: bool
        """
        self.notify.debug(f"[add_player_to_game] Adding player {pid} to game {gid}")

        if self.player_exists(pid):
            if gid in self.games.keys():
                self.active_connections[pid].gid = gid
                self.send_message(pid, dg_deliver_game(self.games[gid]))
                self.games[gid].add_player(pid)
                return True
            else:
                self.notify.warning(f"[add_player_to_game] Attempted to add player {pid} to "
                                    f"non-existent game {gid}")
        else:
            self.notify.warning(f"[add_player_to_game] Attempted to add non-existent player {pid} to "
                                f"game {gid}")
        return False

    def remove_player_from_game(self, pid, reason):
        """
        Removes a player from a game
        @param pid: the player ID of the player leaving the game
        @type pid: int
        @param reason: the reason they're being removed from the game (see 3- codes)
        @type reason: int
        """
        self.notify.debug(f"[remove_player_from_game] Removing player {pid}")

        game = self.game_from_player(pid)
        if game:
            game.remove_player(pid=pid)
            self.active_connections[pid].gid = None
            self.cWriter.send(dg_kick_from_game(reason), self.active_connections[pid].connection)
            return True
        else:
            self.notify.warning(f"[remove_player_from_game] Player {pid} not in game! ({game})")
        return False

    def player_exists(self, pid):
        """
        Check if Player with PID exists
        @param pid: Player ID
        @type pid: int
        @return: If PID exists
        @rtype: bool
        """
        if pid in self.active_connections.keys():
            return True
        return False

    def gid_from_player(self, pid):
        """
        Get a GID from a PID
        @param pid: The Player ID
        @type pid: int
        @return: GID, or None if failed
        @rtype: int
        """
        if self.player_exists(pid):
            if self.active_connections[pid].gid:
                return self.active_connections[pid].gid
            else:
                self.notify.warning(f"[gid_from_player] Attempted to find a GID for player {pid}, who isn't"
                                    f" in a game!")
        else:
            self.notify.warning(f"[gid_from_player] Attempted to get GID from non-existent player {pid}!")
        return None

    def game_from_player(self, pid):
        """
        Get a Game Object from a PID
        @param pid: Player ID
        @type pid: int
        @return: The Game Object, or None if non-existent
        @rtype: Game
        """
        gid = self.gid_from_player(pid)
        if gid:
            if gid in self.games.keys():
                return self.games[gid]
            else:
                self.notify.warning(f"[game_from_player] Player {pid} is in non-existent game {gid}")
        else:
            self.notify.warning(f"[game_from_player] Requested game from player {pid}, who isn't in a game")
        return None

    def remove_player(self, pid, reason):
        """
        remove a player from The System
        @param reason: the reason they're being removed from the game (see 3- codes)
        @type reason: int
        @param pid: the player ID
        @type pid: int
        @return: if successful
        @rtype: bool
        """
        self.notify.debug(f"[remove_player] Removing player {pid} from The System")

        if self.player_exists(pid):
            # remove them from a game if they're in one
            if self.gid_from_player(pid):
                self.remove_player_from_game(pid, reason)

            # tell them in case they don't know
            self.cWriter.send(dg_kill_connection(), self.active_connections[pid].connection)

            # delete
            del self.active_connections[pid]
            return True
        else:
            self.notify.warning(f"[remove_player] Requested to remove non-existent player {pid}")
        return False

    def send_message(self, pid, dg):
        """
        Sends a message to a client
        @param pid: the PID of the player you want to message
        @type pid: int
        @param dg: the datagram you want to send
        @type dg: PyDatagram
        @return: if successful
        @rtype: bool
        """
        if self.player_exists(pid):
            self.cWriter.send(dg, self.active_connections[pid].connection)
            return True
        else:
            self.notify.warning(f"[send_message] Attempted to send message to non-existent player {pid}")
        return False

    def create_pid(self):
        """
        Create a new PID
        @return: a new, unique PID
        @rtype: int
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
        @return: if successful
        @rtype: bool
        """
        try:
            pid = iterator.getUint16()
        except AssertionError:
            self.notify.warning("[request_game] Received invalid REQUEST_GAME")
            return False

        self.notify.debug(f"[request_game] Player {pid} has requested a game!")

        if self.player_exists(pid):
            if not self.gid_from_player(pid):
                game = None

                for g in self.games:
                    # make sure game meets our qualifications
                    if self.games[g].open and not self.games[g].started:
                        game = self.games[g]
                        break

                if game:
                    self.add_player_to_game(pid, game.gid)
                else:
                    self.notify.debug("[request_game] No available games, make one")
                    self.create_game(pid)
                return True
            else:
                self.notify.warning(f"[request_game] {pid} requested game while already in a game")
        else:
            self.notify.warning(f"[request_game] Non-existent player {pid} requested a game!")
        return False

    #TODO add bool
    def vote_to_start(self, iterator):
        """
        Called when a player votes to start the game
            uint16 - pid: the client's player ID
        @return: if successful
        @rtype: bool
        """
        try:
            pid = iterator.getUint16()
        except AssertionError:
            self.notify.warning("[vote_to_start] Received invalid VOTE_TO_START")
            return False

        self.notify.debug(f"[vote_to_start] Player {pid} has voted to start!")

        game = self.gid_from_player(pid)

        if game:
            self.games[game].vote_to_start(pid)
            return True
        else:
            self.notify.warning(f"[vote_to_start] {pid} voted to start without being in a game!")
        return False

    def leave_lobby(self, iterator):
        """
        Called when people tell the server they're leaving the lobby
            uint16 - pid: the player ID
        @return: if successful
        @rtype: bool
        """
        try:
            pid = iterator.getUint16()
        except AssertionError:
            self.notify.warning("[leave_lobby] Received invalid LEAVE_LOBBY")
            return False

        self.notify.debug(f"[leave_lobby] Player {pid} has left their lobby!")

        return self.remove_player_from_game(pid, LEFT_GAME)

    def set_room(self, iterator):
        """
        Called when a player tells the server what room they want to be in
            uint16 - pid: the player ID
            uint8 - room: the room the player wants to be in
        @return: if successful
        @rtype: bool
        """
        try:
            pid = iterator.getUint16()
            room = iterator.getUint8()
        except AssertionError:
            self.notify.warning("[set_room] Received invalid SET_ROOM")
            return False

        self.notify.debug(f"[set_room] Player {pid} is setting their room to {room}")

        game = self.game_from_player(pid)
        if game:
            return game.set_player_room(pid, room)
        return False

    def set_kill(self, iterator):
        """
        Called when a player (who is a killer) tells the server if they want to kill
            uint16 - pid: the player ID
            bool - choice: the player's choice of killing
        @return: if successful
        @rtype: bool
        """
        try:
            pid = iterator.getUint16()
            choice = iterator.getBool()
        except AssertionError:
            self.notify.warning("[set_kill] Received invalid SET_KILL")
            return False

        self.notify.debug(f"[set_kill] Player {pid} is setting their kill choice to {choice}")

        game = self.game_from_player(pid)

        if game:
            return game.set_kill_choice(pid, choice)
        return False

    def heartbeat(self, iterator):
        """
        Heartbeat to keep client connected
            uint16 - pid: the player ID
        @return: if successful
        @rtype: bool
        """
        try:
            pid = iterator.getUint16()
        except AssertionError:
            self.notify.warning("Received invalid HEARTBEAT")
            return False

        self.active_connections[pid].heartbeat = True
        return True

    def goodbye(self, iterator):
        """
        Called when the client closes the connection
            uint16 - pid: the player ID
        @return: if successful
        @rtype: bool
        """
        try:
            pid = iterator.getUint16()
        except AssertionError:
            self.notify.warning("Received invalid GOODBYE")
            return False
        self.notify.debug(f"[goodbye] Received goodbye from {pid}")

        return self.remove_player(pid, CLIENT_LOG_OFF)

    def update_name(self, iterator):
        """
        Called when a player says they want to change their name
        @return: if successful
        @rtype: bool
        """
        try:
            pid = iterator.getUint16()
            new_name = iterator.getString()
        except AssertionError:
            self.notify.warning("Received invalid UPDATE_NAME")
            return False
        self.notify.debug(f"[update_name] Player {pid} is updating their name to {new_name}")

        game = self.game_from_player(pid)
        if game:
            return game.set_name(pid=pid, name=new_name)
        return False

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
