from level.level import Level
from direct.gui.OnscreenText import OnscreenText
from direct.gui.DirectGui import DirectCheckButton
from objects.timer import Timer
from communications.datagrams import dg_set_kill


# Level that all come together during day
class NightLevel(Level):

    multifiles = []

    def __init__(self, father):
        Level.__init__(self, "Night", self.multifiles, father)
        self.players_here = 0

    def create(self):
        txt_night = OnscreenText(text="it is night", pos=(0, -0.75), scale=0.2, fg=(1, 1, 1, 1))
        self.text.append(txt_night)

        txt_num_here = OnscreenText(text="You share the room\n with {} others".format(self.players_here),
                                    pos=(0, .25), scale=0.1, fg=(1, 1, 1, 1))
        self.text.append(txt_num_here)

        # Kill button
        if self.father.killer:
            btn_kill = DirectCheckButton(text="Kill", scale=0.1, command=self.kill)
            self.gui.append(btn_kill)

        # timer
        self.timer = Timer()
        self.timer.start()

    def set_players_here(self, num_here):
        self.players_here = num_here

    def kill(self, status):
        self.father.write(dg_set_kill(self.father.pid, status))
