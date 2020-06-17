from level.mainmenu import MainMenuLevel
from level.day import DayLevel
from level.lobby import LobbyLevel
from level.night import NightLevel
from objects.alert import Alert
from direct.directnotify.DirectNotifyGlobal import directNotify
from communications.datagrams import dg_goodbye
from panda3d.core import VirtualFileSystem
from panda3d.core import Filename
import sys
import atexit


# The Father object holds all UIs and Levels
class Father:
    def __init__(self, _cWriter, _cManager, _cReader):
        # notify
        self.notify = directNotify.newCategory("father")

        # Create stuff we don't want to keep recreating because of their permanence
        self.levels = []
        self.rooms = []
        self.players = {}
        self.dead = []
        self.day = 1
        self.game = None
        self.killer = False
        self.vfs = VirtualFileSystem.getGlobalPtr()

        # this is used in nearly every level, just keep it loaded
        self.vfs.mount(Filename("mf/pawns.mf"), ".", VirtualFileSystem.MFReadOnly)

        # Levels
        self.level_main_menu = MainMenuLevel(self)
        self.level_day = DayLevel(self)
        self.level_lobby = LobbyLevel(self)
        self.level_night = NightLevel(self)

        # Add levels to array
        self.levels.append(self.level_main_menu)
        self.levels.append(self.level_day)
        self.levels.append(self.level_lobby)
        self.levels.append(self.level_night)

        # Set active level
        self.active_level = self.level_main_menu
        self.active_level.create()

        # so we can send messages
        self.my_connection = None
        self.cWriter = _cWriter
        self.cManager = _cManager
        self.cReader = _cReader
        self.pid = None

        atexit.register(self.exit_game)

    def set_active_level(self, level):
        self.active_level.destroy()

        base.camera.setPos((0, 0, 0))
        base.camera.setHpr((0, 0, 0))

        # TODO better way to do this
        for l in self.levels:
            if l.name == level:
                self.active_level = l

        self.active_level.create()

    def add_player(self, local_id):
        """
        Adds a player to the self.players dict
        @param local_id: the local id of the new player
        @type local_id: int
        """
        self.players[local_id] = {"name": "???"}

        if self.active_level.name == "Lobby":
            self.level_lobby.update_player()
            print("Added player {}".format(local_id))

    def remove_player(self, local_id):
        """
        Removes a player from the self.players dict
        @param local_id: the local id of the ex-player
        @type local_id: int
        """
        if self.active_level.name == "Lobby":
            self.players.pop(local_id)
            self.level_lobby.update_player()

    def update_name(self, local_id, new_name):
        """
        Called when a player's name is changed
        @param local_id: The local ID of the player who's name is changing
        @type local_id: int
        @param new_name: The player's new name
        @type new_name: string
        """
        if self.active_level.name == "Lobby":
            self.players[local_id] = {"name": new_name}
            self.level_lobby.update_player()

    def goto_day(self, day_count):
        self.notify.debug("Setting time to day")
        self.day = day_count
        self.set_active_level("Day")

    def goto_night(self):
        self.notify.debug("Setting time to night")
        self.set_active_level("Night")

    def exit_game(self):
        if not self.my_connection:
            sys.exit()

        # tell server
        self.write(dg_goodbye(self.pid))
        self.cManager.closeConnection(self.my_connection)
        sys.exit()

    def failed_to_connect(self):
        """
        Call this when connection to server fails
        """
        self.level_main_menu.failed_to_connect()

    def check_connection(self):
        """
        Checks if we are currently connected
        @return: If we are currently connected
        @rtype: bool
        """
        try:
            if self.my_connection:
                return True
        except AttributeError:
            return False
        return False

    def write(self, dg):
        """
        Sends message to server
        @param dg: datagram you want to send
        @type dg: direct.distributed.PyDatagram.PyDatagram
        @return: if message sends
        @rtype: bool
        """
        if self.my_connection:
            return self.cWriter.send(dg, self.my_connection)
        else:
            Alert(-2)
            self.notify.error("No connection to send message to!")
        return False
