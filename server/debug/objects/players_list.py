from direct.showbase.DirectObject import DirectObject
from objects.notifier import Notifier
from direct.task.TaskManagerGlobal import taskMgr
from direct.gui.OnscreenText import OnscreenText
from direct.gui.DirectGui import DirectButton
from debug.objects.list import List


class PlayersList(Notifier, List):
    def __init__(self, debug_ui):
        """
        :param players: Dict of every player to include in the list
        :type players: dict
        """
        List.__init__(self, debug_ui.messager.active_connections, 10, (-1.1, 0.6), active=False)
        Notifier.__init__(self, "ui-players-list")

        self.debug_ui = debug_ui

        self.btn_players_title = DirectButton(scale=self.scale, text="Players", pos=(-.65, 1, .8),
                                              frameSize=self.frame_size,
                                              command=self.debug_ui.switch_list, extraArgs=[2])

        self.notify.info("[__init__] Created a PlayersList")
