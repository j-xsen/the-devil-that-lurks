from direct.showbase.ShowBase import ShowBase
from panda3d.core import *

from father import Father

class MyApp(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)
        ShowBase.set_background_color(self, 0.08, 0.08, 0.08, 1)
        render.setAntialias(AntialiasAttrib.MAuto)
        self.disableMouse()

        self.father = Father()

app = MyApp()

app.run()
