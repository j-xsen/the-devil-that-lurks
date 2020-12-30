from direct.showbase.DirectObject import DirectObject
from direct.directnotify.DirectNotifyGlobal import directNotify
from debug.objects.games_list import GamesList


class DebugUI(DirectObject):

    def __init__(self, messager):
        DirectObject.__init__(self)

        self.notify = directNotify.newCategory("ui")

        self.games_list = GamesList()

        self.notify.debug("__init__ Created DebugUI")
