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
        self.accept('escape', self.debug)

        # try to connect
        self.connect()

    def debug(self):
        self.notify.info("Debug")
        self.father.set_active_level("Main Menu")

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
                msg_id = iterator.getUint8()

                # Received PID
                if msg_id == DELIVER_PID:
                    if not self.father.pid:
                        pid = iterator.getUint16()
                        self.notify.info("Received PID: {}".format(pid))
                        self.father.pid = pid
                    else:
                        self.notify.warning("Received PID after already receiving one")

                # Received Game
                elif msg_id == DELIVER_GAME:
                    # if father is on main menu, send them to lobby
                    if self.father.active_level.name == "Main Menu":
                        self.father.set_active_level("Lobby")
                        self.father.active_level.update_player_count(iterator.getUint8())
                        self.father.active_level.update_vote_count(iterator.getUint8())
                    else:
                        self.notify.warning("Received a game while in a game")

                # Kicked From Game
                elif msg_id == KICKED_FROM_GAME:
                    self.notify.info("Removed from game")
                    self.father.set_active_level("Main Menu")

                # Received Player Count Update
                elif msg_id == UPDATE_PLAYER_COUNT:
                    if self.father.active_level.name == "Lobby":
                        self.father.active_level.update_player_count(iterator.getUint8())

                # Received Vote Count Update
                elif msg_id == UPDATE_VOTE_COUNT:
                    if self.father.active_level.name == "Lobby":
                        self.father.active_level.update_vote_count(iterator.getUint8())

                # Received Start Game
                elif msg_id == START_GAME:
                    if self.father.active_level.name == "Lobby":
                        self.father.set_active_level("Day")
                    else:
                        self.notify.warning("Received start game signal while in {}"
                                            .format(self.father.active_level.name))

                # Day/Night Cycle
                elif msg_id == CHANGE_TIME:
                    if self.father.active_level.name != "Main Menu":
                        self.father.change_time(iterator.getBool())
                    else:
                        self.notify.warning("Received CHANGE_TIME while not in game")

                # Error
                else:
                    self.notify.warning("Unknown msg_id: {}".format(msg_id))
        return Task.cont


app = Client()
app.run()
