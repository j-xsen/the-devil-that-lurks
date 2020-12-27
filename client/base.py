from direct.showbase.ShowBase import ShowBase
from panda3d.core import AntialiasAttrib, loadPrcFileData
from direct.task.TaskManagerGlobal import taskMgr
from direct.directnotify.DirectNotifyGlobal import directNotify

# networking
from panda3d.core import QueuedConnectionManager
from panda3d.core import QueuedConnectionListener
from panda3d.core import QueuedConnectionReader
from panda3d.core import ConnectionWriter

from communications.codes import *
from father import Father
from communications.messager import Messager
from objects.alert import Alert
from level.codes import *

from config import *
from panda3d.core import loadPrcFile
loadPrcFile("config/Config.prc")

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
        self.father = Father(self.cWriter, self.cManager, self.cReader)

        # inputs
        self.accept('escape', self.debug)

        # try to connect
        self.connect()

    def debug(self):
        # testing_alert = Alert(-1)
        self.father.set_active_level(NIGHT)

    def connect(self):
        port_address = SERVER_PORT
        ip_address = SERVER_IP
        timeout = 3000

        my_connection = self.cManager.openTCPClientConnection(ip_address,
                                                              port_address,
                                                              timeout)
        if my_connection:
            self.notify.info("Connected")
            self.father.set_connection(my_connection)
            self.cReader.addConnection(my_connection)

            # tasks
            taskMgr.add(self.father.messager.check_for_message, "Poll the connection reader", -39)
            taskMgr.doMethodLater(HEARTBEAT_PLAYER, self.father.messager.heartbeat, "Send heartbeat")
        else:
            Alert(-2)
            self.father.failed_to_connect()
            self.notify.warning("Could not connect!")


app = Client()
app.run()
