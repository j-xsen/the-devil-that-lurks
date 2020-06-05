from direct.showbase.ShowBase import ShowBase
from panda3d.core import AntialiasAttrib, loadPrcFileData
from direct.task.TaskManagerGlobal import taskMgr, Task
from direct.directnotify.DirectNotifyGlobal import directNotify
import sys

# networking
from panda3d.core import QueuedConnectionManager
from panda3d.core import QueuedConnectionListener
from panda3d.core import QueuedConnectionReader
from panda3d.core import ConnectionWriter
from panda3d.core import NetDatagram
from direct.distributed.PyDatagramIterator import PyDatagramIterator

from codes import *
from father import Father
from communicator import dg_send_heartbeat, dg_goodbye
from objects.alert import Alert

from codes import NUM_IN_ROOM

loadPrcFileData("", "\n".join(["notify-level-lp debug",
                               "notify-level-father debug",
                               "notify-level-gui-alert debug"]))


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
        self.father = Father(self.cWriter, self.cManager)

        # inputs
        self.accept('escape', self.debug)

        # try to connect
        self.connect()

    def debug(self):
        self.notify.debug("Debug")
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
            taskMgr.doMethodLater(HEARTBEAT_PLAYER, self.heartbeat, "Send heartbeat")
        else:
            self.notify.info("Could not connect!")

    def heartbeat(self, taskdata):
        self.father.write(dg_send_heartbeat(self.father.pid))
        return Task.again

    def tsk_reader(self, taskdata):
        if self.cReader.dataAvailable():
            dg = NetDatagram()
            if self.cReader.getData(dg):
                iterator = PyDatagramIterator(dg)

                try:
                    msg_id = iterator.getUint8()
                except AssertionError:
                    self.notify.warning("Invalid msg_id")
                    return Task.cont

                # Received PID
                if msg_id == DELIVER_PID:
                    if not self.father.pid:
                        try:
                            pid = iterator.getUint16()
                        except AssertionError:
                            self.notify.warning("Invalid DELIVER_PID")
                            return Task.cont

                        self.notify.debug("Received PID: {}".format(pid))
                        self.father.pid = pid
                    else:
                        self.notify.warning("Received PID after already receiving one")

                # Received Game
                elif msg_id == DELIVER_GAME:
                    # check if valid
                    try:
                        player_count = iterator.getUint8()
                        vote_count = iterator.getUint8()
                    except AssertionError:
                        self.notify.warning("Invalid DELIVER_GAME")
                        return Task.cont

                    # if father is on main menu, send them to lobby
                    if self.father.active_level.name == "Main Menu":
                        self.father.set_active_level("Lobby")
                        self.father.active_level.update_player_count(player_count)
                        self.father.active_level.update_vote_count(vote_count)
                    else:
                        self.notify.warning("Received a game while in a game")

                # Kicked From Game
                elif msg_id == KICKED_FROM_GAME:
                    self.notify.debug("Removed from game")
                    self.father.set_active_level("Main Menu")

                    try:
                        reason = iterator.getUint8()
                    except AssertionError:
                        self.notify.warning("Invalid KICKED_FROM_GAME")
                        return Task.cont

                    # need we tell them that they hit leave game?
                    if reason != LEFT_GAME:
                        Alert(reason)

                # Connection was killed
                elif msg_id == KILLED_CONNECTION:
                    self.notify.debug("Connection has been killed")
                    self.exit_game()

                # Received Player Count Update
                elif msg_id == UPDATE_PLAYER_COUNT:
                    if self.father.active_level.name == "Lobby":
                        try:
                            player_count = iterator.getUint8()
                        except AssertionError:
                            self.notify.warning("Invalid UPDATE_PLAYER_COUNT")
                            return Task.cont

                        self.father.active_level.update_player_count(player_count)

                # Received Vote Count Update
                elif msg_id == UPDATE_VOTE_COUNT:
                    if self.father.active_level.name == "Lobby":
                        try:
                            vote_count = iterator.getUint8()
                        except AssertionError:
                            self.notify.warning("Invalid UPDATE_VOTE_COUNT")
                            return Task.cont

                        self.father.active_level.update_vote_count(vote_count)

                # Received Start Game
                elif msg_id == START_GAME:
                    if self.father.active_level.name == "Lobby":
                        players = {}
                        i = 0
                        while i < MAX_PLAYERS:
                            try:
                                name = iterator.getString()
                                local_id = iterator.getUint8()
                                players[local_id] = {"name": name}
                            except AssertionError:
                                self.notify.warning("Invalid START_GAME")
                                return Task.cont
                            i += 1

                        self.father.players = players
                        self.father.day = 0
                        self.father.set_active_level("Day")
                    else:
                        self.notify.warning("Received start game signal while in {}"
                                            .format(self.father.active_level.name))

                elif msg_id == YOU_ARE_KILLER:
                    self.father.killer = True

                elif msg_id == HAS_DIED:
                    self.notify.debug("Received HAS_DIED")
                    try:
                        the_dead = iterator.getUint8()
                    except AssertionError:
                        self.notify.warning("Invalid HAS_DIED")
                        return Task.cont

                    self.notify.debug("{} is dead".format(the_dead))
                    self.father.dead.append(the_dead)

                # Day/Night Cycle
                elif msg_id == GOTO_DAY:
                    self.notify.debug("Received GOTO_DAY")
                    if self.father.active_level.name != "Main Menu":
                        try:
                            day_count = iterator.getUint8()
                        except AssertionError:
                            self.notify.warning("Invalid GOTO_DAY")
                            return Task.cont

                        self.father.goto_day(day_count)
                    else:
                        self.notify.warning("Received GOTO_DAY while not in game")

                elif msg_id == GOTO_NIGHT:
                    self.notify.debug("Received GOTO_NIGHT")
                    if self.father.active_level.name != "Main Menu":
                        self.father.goto_night()
                    else:
                        self.notify.warning("Received GOTO_NIGHT while not in game")

                elif msg_id == KILL_FAILED_EMPTY_ROOM:
                    self.notify.debug("Failed to kill! Empty room!")

                elif msg_id == NUM_IN_ROOM:
                    self.notify.debug("Received NUM_IN_ROOM")
                    try:
                        num = iterator.getUint8()
                        self.father.level_night.set_players_here(num)
                    except AssertionError:
                        self.notify.warning("Invalid NUM_IN_ROOM")
                        return Task.cont

                # Error
                else:
                    self.notify.warning("Unknown msg_id: {}".format(msg_id))
        return Task.cont


app = Client()
app.run()
