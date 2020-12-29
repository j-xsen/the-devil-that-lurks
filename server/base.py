from direct.showbase.ShowBase import ShowBase
from direct.showbase.RandomNumGen import RandomNumGen
from direct.directnotify.DirectNotifyGlobal import directNotify
from direct.task.TaskManagerGlobal import taskMgr, Task
from panda3d.core import loadPrcFileData
import time

from communications.datagrams import *
from objects.game import Game
from config import *
from communications.messager import Messager

from panda3d.core import loadPrcFile
loadPrcFile("config/Config.prc")


class Server(ShowBase):
    # notify
    notify = directNotify.newCategory("server")

    def __init__(self):
        ShowBase.__init__(self)

        self.messager = Messager()

        # tasks
        taskMgr.add(self.messager.check_for_new_players, "Poll the connection listener", -39)
        taskMgr.add(self.messager.check_for_message, "Poll the connection reader", -40)
        taskMgr.doMethodLater(HEARTBEAT_SERVER, self.messager.check_heartbeats,
                              "Poll connection heartbeats")


app = Server()
app.run()
