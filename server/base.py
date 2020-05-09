from direct.showbase.ShowBase import ShowBase
from direct.showbase.RandomNumGen import RandomNumGen
from direct.directnotify.DirectNotifyGlobal import directNotify
from direct.task.TaskManagerGlobal import taskMgr, Task
from panda3d.core import loadPrcFileData
import time

# network
from panda3d.core import QueuedConnectionManager
from panda3d.core import QueuedConnectionListener
from panda3d.core import QueuedConnectionReader
from panda3d.core import ConnectionWriter
from panda3d.core import PointerToConnection, NetAddress, NetDatagram
from direct.distributed.PyDatagramIterator import PyDatagramIterator

from communicator import *
from objects.game import Game

# no window
loadPrcFileData("", "\n".join(["notify-level-server debug",
                               "notify-level-game debug",
                               "notify-level-ai debug",
                               "window-type none"]))


class Server(ShowBase):
    # notify
    notify = directNotify.newCategory("server")

    # network
    cManager = QueuedConnectionManager()
    cListener = QueuedConnectionListener(cManager, 0)
    cReader = QueuedConnectionReader(cManager, 0)
    cWriter = ConnectionWriter(cManager, 0)

    def __init__(self):
        ShowBase.__init__(self)

        # dict of connections
        self.active_connections = {}

        # dict of games
        self.games = {}

        # connect
        port_address = 9099
        backlog = 1000
        tcpSocket = self.cManager.openTCPServerRendezvous(port_address, backlog)
        self.cListener.addConnection(tcpSocket)

        # tasks
        taskMgr.add(self.tsk_listener_polling, "Poll the connection listener", -39)
        taskMgr.add(self.tsk_reader_polling, "Poll the connection reader", -40)
        taskMgr.doMethodLater(HEARTBEAT_SERVER, self.heartbeat, "Poll connection heartbeats")

    def tsk_listener_polling(self, taskdata):
        if self.cListener.newConnectionAvailable():
            rendezvous = PointerToConnection()
            net_address = NetAddress()
            new_connection = PointerToConnection()

            if self.cListener.getNewConnection(rendezvous, net_address, new_connection):
                self.notify.info("New connection")
                new_connection = new_connection.p()

                pid = RandomNumGen(int(round(time.time() * 1000))).randint(0, 65535)

                self.active_connections[pid] = {"connection": new_connection,
                                                "gid": None,
                                                "heartbeat": True}

                self.cReader.add_connection(new_connection)

                self.cWriter.send(dg_deliver_pid(pid), new_connection)
        return Task.cont

    def tsk_reader_polling(self, taskdata):
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

                # Request a game
                if msg_id == REQUEST_GAME:
                    try:
                        pid = iterator.getUint16()
                        self.request_game(connection, pid)
                    except AssertionError:
                        self.notify.warning("Received invalid REQUEST_GAME")

                # vote to start
                elif msg_id == VOTE_TO_START:
                    try:
                        pid = iterator.getUint16()
                        game = self.get_game_from_pid(pid)
                        if game:
                            game.vote_to_start(pid)
                        else:
                            self.notify.warning("No game for {}".format(pid))
                    except AssertionError:
                        self.notify.warning("Received invalid VOTE_TO_START")

                # leave lobby
                elif msg_id == LEAVE_LOBBY:
                    try:
                        pid = iterator.getUint16()
                        self.remove_player_from_game(pid, LEFT_GAME)
                    except AssertionError:
                        self.notify.warning("Received invalid LEAVE_LOBBY")

                # set room
                elif msg_id == SET_ROOM:
                    try:
                        pid = iterator.getUint16()
                        room = iterator.getUint8()
                        game = self.get_game_from_pid(pid)
                        if game:
                            # client has game, set their room status
                            game.set_player_room(pid, room)
                        else:
                            self.notify.warning("{} attempted set room while not in a game".format(pid))
                    except AssertionError:
                        self.notify.warning("Received invalid SET_ROOM")

                elif msg_id == SET_KILL:
                    try:
                        pid = iterator.getUint16()
                        choice = iterator.getBool()
                    except AssertionError:
                        self.notify.warning("Received invalid SET_KILL")
                        return Task.cont

                    game = self.get_game_from_pid(pid)
                    if game:
                        game.set_kill_choice(pid, choice)
                    else:
                        self.notify.warning("{} attempted to set kill while not in a game".format(pid))

                # send heartbeat
                elif msg_id == HEARTBEAT:
                    try:
                        pid = iterator.getUint16()
                        self.active_connections[pid]["heartbeat"] = True
                    except AssertionError:
                        self.notify.warning("Received invalid HEARTBEAT")

                elif msg_id == GOODBYE:
                    try:
                        self.notify.debug("Received goodbye")
                        pid = iterator.getUint16()
                        self.remove_player(pid)
                    except AssertionError:
                        self.notify.warning("Received invalid GOODBYE")

                else:
                    self.notify.warning("Unknown datagram {}".format(msg_id))
        return Task.cont

    # Client requested a game
    def request_game(self, connection, pid):
        if not self.active_connections[pid]["gid"]:
            if len(self.games) > 0:
                game = None

                for g in self.games:
                    this_game = self.games[g]
                    # make sure game meets our qualifications
                    if this_game.open and not this_game.started:
                        game = this_game
                        break

                if game:
                    self.add_player_to_game(pid, game)
                else:
                    self.notify.debug("No available games, make one")
                    self.create_game(pid)
            else:
                self.notify.debug("No available games, make one")
                self.create_game(pid)
        else:
            self.notify.warning("{} requested game while already in a game".format(pid))

            # remove them from that game
            self.remove_player_from_game(pid, ALREADY_IN_GAME)

    def add_player_to_game(self, pid, game):
        player_thing = self.active_connections[pid]

        player_thing["gid"] = game.get_gid()  # set the active_connection's game for this PID
        connection = player_thing["connection"]  # get the connection
        game.add_player(connection, pid)  # add player to game
        self.cWriter.send(dg_deliver_game(game), connection)

    def remove_player_from_game(self, pid, reason):
        self.notify.debug("Removing {} from game".format(pid))
        game = self.get_game_from_pid(pid)
        if game:
            self.get_game_from_pid(pid).remove_player(pid)
        else:
            self.notify.warning("No game for player {}".format(pid))

        self.active_connections[pid]["gid"] = None

        self.cWriter.send(dg_kick_from_game(reason), self.active_connections[pid]["connection"])

    def get_game_from_gid(self, gid):
        if gid in self.games:
            return self.games[gid]
        else:
            return False

    def get_game_from_pid(self, pid):
        gid = self.active_connections[pid]['gid']
        if gid:
            self.notify.debug("Found gid of {} for player {}".format(gid, pid))
            return self.get_game_from_gid(gid)
        else:
            self.notify.warning("Can't find game w/ pid of {}".format(pid))
        return False

    def create_game(self, pid):
        gid = RandomNumGen(int(round(time.time() * 1000))).randint(0, 65535)
        # create game
        game = Game(gid, self.cWriter, self.delete_game, self.remove_player_from_game)

        self.add_player_to_game(pid, game)

        # add game to games dict
        self.games[gid] = game

    def delete_game(self, gid):
        self.notify.info("Delete game: {}".format(gid))

        # remove gid from players
        game = self.get_game_from_gid(gid)
        for p in game.players:
            if not p.ai:
                self.active_connections[p.get_pid()]["gid"] = None

        del self.games[gid]

    # ran every 11 seconds
    def heartbeat(self, taskdata):
        remove = []

        for c in self.active_connections:
            # check if player didn't respond last time
            if not self.active_connections[c]["heartbeat"]:
                # Player failed to reply
                self.notify.debug("Player {} has no heartbeat!". format(c))
                remove.append(c)
            else:
                # player passed
                self.active_connections[c]["heartbeat"] = False

        # delete the dead ones
        for r in remove:
            self.remove_player(r)

        return Task.again

    def remove_player(self, pid):
        game = self.get_game_from_pid(pid)
        if game:
            game.remove_player(pid)

        self.cWriter.send(dg_kill_connection(), self.active_connections[pid]["connection"])
        del self.active_connections[pid]


app = Server()
app.run()
