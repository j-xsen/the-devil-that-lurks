from level.level import Level

from direct.gui.OnscreenText import OnscreenText

class LobbyLevel(Level):
    def __init__(self, father):
        Level.__init__(self, "Lobby", "img/egg/mainmenu.egg", father)

    def create(self):
        textObject = OnscreenText(text="Lobby", pos=(0,0.5), scale=0.35, fg=(1,1,1, 1))
        self.text.append(textObject)