from level.level import Level
from direct.gui.OnscreenText import OnscreenText
from direct.gui.DirectGui import DirectCheckButton
from objects.timer import Timer
from communications.datagrams import dg_set_kill


class NightLevel(Level):

    multifiles = []

    def __init__(self, father):
        Level.__init__(self, "Night", self.multifiles, father)
        self.players_here = 0

    def create(self):
        # Debug text
        txt_night = OnscreenText(text="it is night", pos=(0, -0.75), scale=0.2, fg=(1, 1, 1, 1))

        # Text displaying number players here
        txt_num_here = OnscreenText(text="You share the room\n with {} others".format(self.players_here),
                                    pos=(0, .25), scale=0.1, fg=(1, 1, 1, 1))

        self.text["txt_night"] = txt_night
        self.text["txt_num_here"] = txt_num_here

        # Kill button
        if self.level_holder.killer:
            btn_kill = DirectCheckButton(text="Kill", scale=0.1, command=self.kill)
            self.gui["btn_kill"] = btn_kill

        # timer
        self.timer = Timer(2)

    def kill(self, status):
        self.messager.write(dg_set_kill(self.messager.pid, status))
