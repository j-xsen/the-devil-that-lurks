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

# no window
# loadPrcFileData("", "window-type none")
loadPrcFileData("", "\n".join(["notify-level-server debug",
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
            datagram = NetDatagram()
            if self.cReader.getData(datagram):
                # TODO: Proccess data
                pass
        return Task.cont


app = Server()
app.run()
