from level.level import Level
from direct.gui.OnscreenText import OnscreenText
from objects.timer import Timer


# Level that all come together during day
class NightLevel(Level):
    def __init__(self, father):
        Level.__init__(self, "Night", "img/egg/mainmenu.egg", father)

    def create(self):
        txt_night = OnscreenText(text="it is night", pos=(0, -0.75), scale=0.2, fg=(1, 1, 1, 1))
        self.text.append(txt_night)

        # timer
        self.timer = Timer()
        self.timer.start()
