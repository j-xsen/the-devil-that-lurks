from level.mainmenu import MainMenuLevel
from level.day import DayLevel
from level.lobby import LobbyLevel
from level.night import NightLevel
from direct.directnotify.DirectNotifyGlobal import directNotify
from communicator import dg_goodbye
import sys
import atexit


# The Father object holds all UIs and Levels
class Father:
    def __init__(self, _cWriter, _cManager):
        # notify
        self.notify = directNotify.newCategory("father")

        # Create stuff we don't want to keep recreating because of their permanence
        self.levels = []
        self.rooms = []
        self.players = {}
        self.day = 0
        self.game = None

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
        self.pid = None

        atexit.register(self.exit_game)

    def set_active_level(self, level):
        self.active_level.destroy()

        base.camera.setPos((0, 0, 0))
        base.camera.setHpr((0, 0, 0))

        for l in self.levels:
            if l.name == level:
                self.active_level = l

        self.active_level.create()

    def change_time(self, time, day_count):
        if time:
            self.notify.debug("Setting time to day")
            self.set_active_level("Day")
            self.active_level.set_day_count(day_count)
        else:
            self.notify.debug("Setting time to night")
            self.set_active_level("Night")

    def exit_game(self):
        # tell server
        self.write(dg_goodbye(self.pid))
        self.cManager.closeConnection(self.my_connection)
        sys.exit()

    # use this to send messages to server
    def write(self, dg):
        if self.my_connection:
            self.cWriter.send(dg, self.my_connection)
        else:
            self.notify.error("No connection to send message to!")
