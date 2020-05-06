from level.mainmenu import MainMenuLevel
from level.loading import LoadingLevel
from level.livingroom import LivingRoomLevel
from level.lobby import LobbyLevel
from player import Player
from direct.directnotify.DirectNotifyGlobal import directNotify


# The Father object holds all UIs and Levels
class Father:
    def __init__(self, cWriter):
        # notify
        self.notify = directNotify.newCategory("father")

        # Create stuff we don't want to keep recreating because of their permanence
        self.levels = []
        self.rooms = []
        self.players = []
        self.day = 0
        self.game = None

        # Levels
        self.level_main_menu = MainMenuLevel(self)
        self.level_loading = LoadingLevel(self)
        self.level_living_room = LivingRoomLevel(self)
        self.level_lobby = LobbyLevel(self)

        # Add levels to array
        self.levels.append(self.level_main_menu)
        self.levels.append(self.level_loading)
        self.levels.append(self.level_living_room)
        self.levels.append(self.level_lobby)

        # Set active level
        self.active_level = self.level_main_menu
        self.active_level.create()

        # so we can send messages
        self.my_connection = None
        self.cWriter = cWriter
        self.pid = None

    def set_active_level(self, level):
        self.active_level.destroy()

        base.camera.setPos((0, 0, 0))
        base.camera.setHpr((0, 0, 0))

        for l in self.levels:
            if l.name == level:
                self.active_level = l

        self.active_level.create()

    # use this to send messages to server
    def write(self, dg):
        if self.my_connection:
            self.cWriter.send(dg, self.my_connection)
        else:
            self.notify.error("No connection to send message to!")
