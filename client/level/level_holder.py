from level.mainmenu import MainMenuLevel
from level.day import DayLevel
from level.lobby import LobbyLevel
from level.night import NightLevel
from objects.alert import Alert
from direct.directnotify.DirectNotifyGlobal import directNotify
from communications.datagrams import dg_goodbye
from panda3d.core import VirtualFileSystem
from panda3d.core import Filename
from objects.player import Player
import sys
import atexit
from level.codes import *
from communications.messager import Messager


# The Father object holds all UIs and Levels
class LevelHolder:

    def __init__(self, _cWriter, _cManager, _cReader):
        # notify
        self.notify = directNotify.newCategory("level_holder")

        # so we can send messages
        self.messager = Messager(_cWriter, _cManager, _cReader, self)

        # Create stuff we don't want to keep recreating because of their permanence
        self.players = {}
        self.day = 0
        self.killer = False
        self.red_room = 0
        self.vfs = VirtualFileSystem.getGlobalPtr()

        # these are used in nearly every level, just keep it loaded
        self.vfs.mount(Filename("mf/pawns.mf"), ".", VirtualFileSystem.MFReadOnly)
        self.vfs.mount(Filename("mf/timer.mf"), ".", VirtualFileSystem.MFReadOnly)

        # Levels
        self.levels = {
            MAINMENU: MainMenuLevel(self),
            LOBBY: LobbyLevel(self),
            DAY: DayLevel(self),
            NIGHT: NightLevel(self)
        }

        # Set active level
        self.active_level = MAINMENU
        self.levels[self.active_level].create()

        atexit.register(self.exit_game)

        self.notify.debug("[__init__] Created level_holder")

    def set_active_level(self, level):
        """
        Set the active level
        @param level: the level's code
        @param day_count: (opt) if day_count has been updated
        @type level: int
        """
        self.levels[self.active_level].destroy()

        base.camera.setPos((0, 0, 0))
        base.camera.setHpr((0, 0, 0))

        self.active_level = level

        self.levels[self.active_level].create()

    def add_player(self, local_id, name):
        """
        Adds a player to the self.players dict
        """
        new_player = Player(local_id, name=name)
        self.players[local_id] = new_player

        self.notify.debug(f"[add_player] Added local player {local_id}")

        if self.active_level == LOBBY:
            self.levels[LOBBY].update_player()

    def remove_player(self, local_id):
        """
        Removes a player from the self.players dict
        @param local_id: the local id of the ex-player
        @type local_id: int
        """
        if self.active_level == LOBBY:
            self.players.pop(local_id)
            self.levels[LOBBY].update_player()

    def update_name(self, local_id, new_name):
        """
        Called when a player's name is changed
        @param local_id: The local ID of the player who's name is changing
        @type local_id: int
        @param new_name: The player's new name
        @type new_name: string
        @return: If successful
        @rtype: bool
        """
        self.notify.debug(f"[update_name] Changing name of {local_id} to {new_name}")
        if self.active_level == LOBBY:
            self.players[local_id].name = new_name
            self.levels[LOBBY].update_player()
            return True
        return False

    def reset_game_vars(self):
        """
        Erases all game variables so you can start fresh
        """
        self.players = {}
        self.day = 0
        self.killer = False

    def exit_game(self):
        """
        Use this to close the game.
        Closes connection and tells server we're leaving
        """
        VirtualFileSystem.getGlobalPtr().unmount("mf/pawns.mf")
        VirtualFileSystem.getGlobalPtr().unmount("mf/timer.mf")

        for level in self.levels:
            self.levels[level].destroy()

        if not self.messager.my_connection or not self.messager.pid:
            sys.exit()

        # tell server
        self.write(dg_goodbye(self.messager.pid))
        self.messager.cManager.closeConnection(self.messager.my_connection)
        sys.exit()

    def set_connection(self, connection):
        self.messager.my_connection = connection

        if self.active_level == MAINMENU:
            self.levels[MAINMENU].connected()

    def failed_to_connect(self):
        """
        Call this when connection to server fails
        Tells the game to back to main menu & display an error
        """
        self.set_active_level(MAINMENU)
        self.levels[MAINMENU].failed_to_connect()

    def check_connection(self):
        """
        Checks if we are currently connected
        @return: If we are currently connected
        @rtype: bool
        """
        try:
            if self.messager.my_connection:
                return True
        except AttributeError:
            return False
        return False

    def write(self, dg):
        """
        forwards this the messager
        """
        return self.messager.write(dg)
