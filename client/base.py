from direct.showbase.ShowBase import ShowBase
from panda3d.core import AntialiasAttrib, loadPrcFileData

# networking
from panda3d.core import QueuedConnectionManager
from panda3d.core import QueuedConnectionListener
from panda3d.core import QueuedConnectionReader
from panda3d.core import ConnectionWriter

# threading
from direct.stdpy import threading

from direct.directnotify.DirectNotifyGlobal import directNotify

from father import Father

loadPrcFileData("", "\n".join(["notify-level-lp debug"]))


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
            self.cReader.addConnection(my_connection)
        else:
            self.notify.info("Could not connect!")


app = Client()
app.run()
