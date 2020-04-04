from level.mainmenu import MainMenuLevel
from level.loading import LoadingLevel
from level.livingroom  import LivingRoomLevel
from room import Room
from direct.gui.DirectGui import OnscreenImage
from player import Player

# The Father object holds all UIs and Levels
class Father:
    def __init__(self):
        # Create stuff we don't want to keep recreating because of their permanence
        self.levels = []
        self.rooms = []
        self.players = []
        self.day = 0

        self.level_mainmenu = MainMenuLevel(self)
        self.level_loading = LoadingLevel(self)
        self.level_game = LivingRoomLevel(self)

        self.levels.append(self.level_mainmenu)
        self.levels.append(self.level_loading)
        self.levels.append(self.level_game)

        self.active_level = self.level_mainmenu
        self.active_level.create()

    def set_active_level(self, level):
        self.active_level.destroy()

        base.camera.setPos((0, 0, 0))
        base.camera.setHpr((0, 0, 0))

        for l in self.levels:
            if l.name == level:
                self.active_level = l

        if level == "Game" and self.day == 0:
            self.create_players()
            # self.create_players()

        self.active_level.create()

    def create_players(self):
        self.players.append(Player(0, "Jaxsen", False, True))
        for i in range(0, 9):
            self.players.append(Player(i, i, False, False))