from level.level import Level

from direct.gui.OnscreenText import OnscreenText

class LobbyLevel(Level):
    def __init__(self, father):
        Level.__init__(self, "Lobby", "img/egg/mainmenu.egg", father)

    def create(self):
        players_txt = OnscreenText(text="Players", pos=(0,0.5), scale=0.35, fg=(1,1,1, 1))
        current_txt = OnscreenText(text="0/9", pos=(0,0), scale=0.2, fg=(1,1,1,1))
        self.text.append(current_txt)
        self.text.append(players_txt)