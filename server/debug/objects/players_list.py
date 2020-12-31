from direct.showbase.DirectObject import DirectObject
from objects.notifier import Notifier
from direct.gui.DirectGui import DirectButton
from debug.objects.list import List


class PlayersList(DirectObject, Notifier, List):
    def __init__(self, debug_ui):
        """
        @param debug_ui: The parent DebugUI
        @type debug_ui: DebugUI
        """
        DirectObject.__init__(self)
        List.__init__(self, debug_ui.messager.active_connections, 10, (-1.1, 0.6), active=False,
                      command=debug_ui.change_pid)
        Notifier.__init__(self, "ui-players-list")

        self.debug_ui = debug_ui

        self.btn_title = DirectButton(scale=self.scale, text="Players", pos=(-.65, 1, .8),
                                      frameSize=self.frame_size,
                                      command=self.debug_ui.switch_list, extraArgs=[2])

        self.accept("arrow_right", self.next_page)
        self.accept("arrow_left", self.previous_page)

        self.notify.info("[__init__] Created a PlayersList")
