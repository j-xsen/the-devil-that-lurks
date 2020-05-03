from direct.showbase.ShowBase import ShowBase
from panda3d.core import AntialiasAttrib, loadPrcFileData
from direct.task.TaskManagerGlobal import taskMgr, Task

# networking
from panda3d.core import QueuedConnectionManager
from panda3d.core import QueuedConnectionListener
from panda3d.core import QueuedConnectionReader
from panda3d.core import ConnectionWriter
from panda3d.core import NetDatagram
from direct.distributed.PyDatagramIterator import PyDatagramIterator

from codes import *
from direct.directnotify.DirectNotifyGlobal import directNotify

from father import Father

loadPrcFileData("", "\n".join(["notify-level-lp debug",
                               "notify-level-father debug"]))


class Client(ShowBase):
    # notify
    notify = directNotify.newCategory("lp")

    # network
    cManager = QueuedConnectionManager()
    cListener = QueuedConnectionListener(cManager, 0)
    cReader = QueuedConnectionReader(cManager, 0)
    cWriter = ConnectionWriter(cManager, 0)

    def __init__(self):
        ShowBase.__init__(self)
        ShowBase.set_background_color(self, 0.08, 0.08, 0.08, 1)
        render.setAntialias(AntialiasAttrib.MAuto)
        self.disableMouse()

        # create father
        self.father = Father(self.cWriter)

        # inputs

        # try to connect
        self.connect()

    def connect(self):
        port_address = 9099
        ip_address = "localhost"
        timeout = 3000

        my_connection = self.cManager.openTCPClientConnection(ip_address,
                                                              port_address,
                                                              timeout)
        if my_connection:
            self.notify.info("Connected")
            self.father.my_connection = my_connection
            self.cReader.addConnection(my_connection)

            # poll
            taskMgr.add(self.tsk_reader, "Poll the connection reader", -39)
        else:
            self.notify.info("Could not connect!")

    def tsk_reader(self, taskdata):
        if self.cReader.dataAvailable():
            dg = NetDatagram()
            if self.cReader.getData(dg):
                iterator = PyDatagramIterator(dg)
                if iterator.getUint8() == DELIVER_GAME:
                    # if father is on main menu, send them to lobby
                    if self.father.active_level.name == "Main Menu":
                        self.father.set_active_level("Lobby")
                    else:
                        self.notify.warning("Received a game while in a game")
                else:
                    self.notify.warning("Unknown datagram")
        return Task.cont


app = Client()
app.run()
