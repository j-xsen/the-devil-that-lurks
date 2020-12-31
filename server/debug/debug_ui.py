from direct.showbase.DirectObject import DirectObject
from direct.directnotify.DirectNotifyGlobal import directNotify
from debug.objects.games_list import GamesList
from debug.objects.single_game import SingleGame


class DebugUI(DirectObject):

    def __init__(self, messager):
        DirectObject.__init__(self)

        self.notify = directNotify.newCategory("ui")

        self.messager = messager
        self.games_list = GamesList(self)
        self.single_game = SingleGame(messager)

        self.notify.info("__init__ Created DebugUI")

    def change_gid(self, new_gid):
        self.single_game.change_gid(new_gid)
