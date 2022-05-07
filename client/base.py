from direct.showbase.ShowBase import ShowBase
from panda3d.core import AntialiasAttrib, loadPrcFileData, loadPrcFile, CollisionHandlerEvent, CollisionHandlerQueue
from direct.task.TaskManagerGlobal import taskMgr
from direct.directnotify.DirectNotifyGlobal import directNotify

# networking
from panda3d.core import QueuedConnectionManager
from panda3d.core import QueuedConnectionListener
from panda3d.core import QueuedConnectionReader
from panda3d.core import ConnectionWriter

from communications.codes import *
from level.level_holder import LevelHolder
from communications.messager import Messager
from objects.alert import Alert
from level.codes import *

from config import *

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

        # create collision handler
        self.handler = CollisionHandlerQueue()

        # create level holder
        self.level_holder = LevelHolder(self.cWriter, self.cManager, self.cReader, self.handler)

        # create messager
        self.messager = self.level_holder.messager

        # inputs
        self.accept('escape', self.escape)
        self.accept('mouse1', self.mouse_one)

        # try to connect
        self.connect()

    def escape(self):
        """
        Escape is pressed
        """
        # testing_alert = Alert(-1)
        self.level_holder.exit_game()

    def mouse_one(self):
        """
        Mouse One is pressed
        """
        # First we check that the mouse is not outside the screen.
        if base.mouseWatcherNode.hasMouse():
            # This gives up the screen coordinates of the mouse.
            mpos = base.mouseWatcherNode.getMouse()

            # check if any clickables
            for c in self.level_holder.get_active_level().clickables:
                self.level_holder.get_active_level().clickables[c].beam(mpos, True)

    def connect(self):
        port_address = SERVER_PORT
        ip_address = SERVER_IP
        timeout = 3000

        my_connection = self.cManager.openTCPClientConnection(ip_address,
                                                              port_address,
                                                              timeout)
        if my_connection:
            self.notify.info("Connected")
            self.level_holder.set_connection(my_connection)
            self.cReader.addConnection(my_connection)

            # tasks
            taskMgr.add(self.messager.check_for_message, "Poll the connection reader", -39)
            taskMgr.doMethodLater(HEARTBEAT_PLAYER, self.messager.heartbeat, "Send heartbeat")
        else:
            Alert(-2)
            self.level_holder.failed_to_connect()
            self.notify.warning("Could not connect!")


app = Client()
app.run()
