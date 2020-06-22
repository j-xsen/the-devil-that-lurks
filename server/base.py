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

# no window
loadPrcFileData("", "\n".join(["notify-level-server debug",
                               "notify-level-game debug",
                               "notify-level-ai debug",
                               "notify-level-msgr debug",
                               "window-type none"]))


class Server(ShowBase):
    # notify
    notify = directNotify.newCategory("server")

    def __init__(self):
        ShowBase.__init__(self)

        self.messager = Messager()

        # tasks
        taskMgr.add(self.messager.check_for_new_players, "Poll the connection listener", -39)
        taskMgr.add(self.messager.check_for_message, "Poll the connection reader", -40)
        # taskMgr.doMethodLater(HEARTBEAT_SERVER, self.messager.heartbeat, "Poll connection heartbeats")


app = Server()
app.run()
