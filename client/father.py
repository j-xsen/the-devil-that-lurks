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
        self.level_mainmenu = MainMenuLevel(self)
        self.level_loading = LoadingLevel(self)
        self.level_game = LivingRoomLevel(self)
        self.level_lobby = LobbyLevel(self)

        # Add levels to array
        self.levels.append(self.level_mainmenu)
        self.levels.append(self.level_loading)
        self.levels.append(self.level_game)
        self.levels.append(self.level_lobby)

        # Set active level
        self.active_level = self.level_mainmenu
        self.active_level.create()

        # so we can send messages
        self.my_connection = None
        self.cWriter = cWriter

    def set_active_level(self, level):
        self.active_level.destroy()

        base.camera.setPos((0, 0, 0))
        base.camera.setHpr((0, 0, 0))

        for l in self.levels:
            if l.name == level:
                self.active_level = l

        if level == "Game" and self.day == 0:
            self.create_players()

        self.active_level.create()

    def create_players(self):
        # local client
        self.players.append(Player(3, "Jaxsen", False, True))
        for i in range(0, 9):
            if i != 3:
                self.players.append(Player(i, i, False, False))

    def get_local_player(self):
        for p in self.players:
            if p.local_player:
                return p
        return False

    # use this to send messages to server
    def write(self, dg):
        if self.my_connection:
            self.cWriter.send(dg, self.my_connection)
        else:
            self.notify.error("No connection to send message to!")
