# class to connect with and store connection variables
# only one of these should exist

from panda3d.core import QueuedConnectionManager, QueuedConnectionListener, QueuedConnectionReader
from panda3d.core import ConnectionWriter
from direct.task.TaskManagerGlobal import taskMgr
from config import *
from direct.directnotify.DirectNotifyGlobal import directNotify


class Connector:
    notify = directNotify.newCategory("connector")

    def __init__(self):
        self.connection = None
        self.cManager = QueuedConnectionManager()
        self.cListener = QueuedConnectionListener(self.cManager, 0)
        self.cReader = QueuedConnectionReader(self.cManager, 0)
        self.cWriter = ConnectionWriter(self.cManager, 0)

    def connect(self):
        port_address = SERVER_PORT
        ip_address = SERVER_IP
        timeout = 3000

        my_connection = self.cManager.openTCPClientConnection(ip_address,
                                                              port_address,
                                                              timeout)
        if my_connection:
            self.notify.info("Connected")
            self.connection(my_connection)
            self.cReader.addConnection(my_connection)

            # tasks
            taskMgr.add(self.messager.check_for_message, "Poll the connection reader", -39)
            taskMgr.doMethodLater(HEARTBEAT_PLAYER, self.messager.heartbeat, "Send heartbeat")
        else:
            Alert(-2)
            self.father.failed_to_connect()
            self.notify.warning("Could not connect!")

    def check_for_message(self, taskdata):
        """
        Called repeatedly to check if any new messages from server
        This gets the information from said datagram and calls whatever function necessary
        @param self
        @param taskdata
        """
        if self.cReader.dataAvailable():
            dg = NetDatagram()
            if self.cReader.getData(dg):
                iterator = PyDatagramIterator(dg)

                try:
                    msg_id = iterator.getUint8()
                except AssertionError:
                    self.notify.warning("Invalid msg_id")
                    return Task.cont

                if msg_id in self.mapping:
                    self.mapping[msg_id](self, iterator)
                else:
                    self.notify.warning("Unknown msg_id: {}".format(msg_id))
        return Task.cont
