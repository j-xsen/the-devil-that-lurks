from direct.showbase.ShowBase import ShowBase
from direct.directnotify.DirectNotifyGlobal import directNotify
from direct.task.TaskManagerGlobal import taskMgr, Task
from panda3d.core import loadPrcFileData

# network
from panda3d.core import QueuedConnectionManager
from panda3d.core import QueuedConnectionListener
from panda3d.core import QueuedConnectionReader
from panda3d.core import ConnectionWriter
from panda3d.core import PointerToConnection, NetAddress, NetDatagram
from direct.distributed.PyDatagramIterator import PyDatagramIterator

from communicator import *
from game import Game

# no window
loadPrcFileData("", "\n".join(["notify-level-server debug",
                               "notify-level-game debug",
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

        # array of connections
        self.active_connections = []

        # list of games
        self.games = []

        # connect
        port_address = 9099
        backlog = 1000
        tcpSocket = self.cManager.openTCPServerRendezvous(port_address, backlog)
        self.cListener.addConnection(tcpSocket)

        # tasks
        taskMgr.add(self.tsk_listener_polling, "Poll the connection listener", -39)
        taskMgr.add(self.tsk_reader_polling, "Poll the connection reader", -40)

    def tsk_listener_polling(self, taskdata):
        if self.cListener.newConnectionAvailable():
            rendezvous = PointerToConnection()
            net_address = NetAddress()
            new_connection = PointerToConnection()

            if self.cListener.getNewConnection(rendezvous, net_address, new_connection):
                self.notify.info("New connection")
                new_connection = new_connection.p()
                self.active_connections.append(new_connection)
                self.cReader.add_connection(new_connection)
        return Task.cont

    def tsk_reader_polling(self, taskdata):
        if self.cReader.dataAvailable():
            dg = NetDatagram()
            if self.cReader.getData(dg):
                iterator = PyDatagramIterator(dg)
                if iterator.getUint8() == REQUEST_GAME:
                    self.request_game(dg.getConnection())
                else:
                    self.notify.warning("Unknown datagram {}".format(PyDatagramIterator(dg)))
        return Task.cont

    def request_game(self, connection):
        if len(self.games) > 0:
            # there is a game, lets see if its open
            game = None

            for g in self.games:
                if g.open:
                    game = g
                    break

            # make sure it found one
            if game:
                # add client
                game.add_player(connection)
                # send game to client
                self.cWriter.send(dg_deliver_game(), connection)
            else:
                self.notify.info("No available games, make one")
                self.create_game(connection)
        else:
            self.notify.info("No available games, make one")
            self.create_game(connection)

    def create_game(self, connection):
        self.notify.info("Creating game...")
        # create game
        game = Game()

        # add player
        game.add_player(connection)

        # add game to games array
        self.games.append(game)

        # send to client
        self.cWriter.send(dg_deliver_game(), connection)


app = Server()
app.run()
