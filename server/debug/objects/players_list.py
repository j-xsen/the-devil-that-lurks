from direct.showbase.DirectObject import DirectObject
from objects.notifier import Notifier
from direct.task.TaskManagerGlobal import taskMgr
from direct.gui.OnscreenText import OnscreenText
from direct.gui.DirectGui import DirectButton


class PlayersList(Notifier):
    def __init__(self, players):
        """
        :param players: List of every player to include in the list
        :type players: list
        """
        Notifier.__init__(self, "ui-players-list")
        self.txt_players_title = OnscreenText(text="Players:", pos=(-1, .8), scale=0.1, fg=(1, 1, 1, 1))
        self.btns_players = []
        self.page = 1
        self.max_per_page = 10

        self.notify.info("__init__ Created a PlayersList")
