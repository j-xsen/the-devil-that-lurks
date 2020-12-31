from direct.showbase.DirectObject import DirectObject
from debug.objects.games_list import GamesList
from debug.objects.single_game import SingleGame
from debug.objects.players_list import PlayersList
from objects.notifier import Notifier


class DebugUI(DirectObject, Notifier):

    def __init__(self, messager):
        DirectObject.__init__(self)
        Notifier.__init__(self, "ui")

        self.messager = messager
        self.games_list = GamesList(self)
        self.single_game = SingleGame(messager)
        # self.players_all = PlayersList(message.)

        self.notify.info("__init__ Created DebugUI")

    def change_gid(self, new_gid):
        self.single_game.change_gid(new_gid)
