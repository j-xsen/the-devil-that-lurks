from direct.showbase.DirectObject import DirectObject
from direct.gui.OnscreenText import OnscreenText
from direct.gui.DirectGui import DirectButton
from objects.notifier import Notifier
from debug.objects.list import List


class GamesList(DirectObject, List, Notifier):
    def __init__(self, debug_ui):
        DirectObject.__init__(self)
        Notifier.__init__(self, "ui-games-list")
        List.__init__(self, debug_ui.messager.games, 10, (-1.1, 0.6), command=self.game_clicked)

        self.debug_ui = debug_ui

        self.btn_games_title = DirectButton(scale=self.scale, text="Games", pos=(-1.1, 1, .8),
                                            frameSize=self.frame_size,
                                            command=self.debug_ui.switch_list, extraArgs=[1])

        self.accept("arrow_right", self.next_page)
        self.accept("arrow_left", self.previous_page)

        self.notify.info("[__init__] Created GamesList")

    def game_clicked(self, gid):
        self.notify.info(f"[game_clicked] Clicked game {gid}")
        self.debug_ui.change_gid(gid)
        pass
