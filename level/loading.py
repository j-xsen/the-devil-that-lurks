from level.level import Level

from direct.gui.DirectGui import OnscreenImage

class LoadingLevel(Level):
    def __init__(self, father):
        Level.__init__(self, "Loading", "img/egg/loading.egg", father)

    def create(self):
        print("Created loading")
        red = OnscreenImage(image='img/png/red.png', pos=(0, 0, 0.625), scale=(50, 50, 50))
        self.images.append(red)
