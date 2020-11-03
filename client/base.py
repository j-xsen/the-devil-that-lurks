from direct.showbase.ShowBase import ShowBase
from panda3d.core import AntialiasAttrib, loadPrcFileData
from direct.directnotify.DirectNotifyGlobal import directNotify

from communications.codes import *
from father import Father
from communications.messager import Messager
from objects.alert import Alert
from level.codes import *

loadPrcFileData("", "\n".join(["notify-level-lp debug",
                               "notify-level-father debug",
                               "notify-level-gui-alert debug",
                               "notify-level-msgr debug",
                               "notify-level-connector debug"]))


class Client(ShowBase):
    # notify
    notify = directNotify.newCategory("lp")

    def __init__(self):
        ShowBase.__init__(self)
        ShowBase.set_background_color(self, 0.08, 0.08, 0.08, 1)
        render.setAntialias(AntialiasAttrib.MAuto)
        self.disableMouse()

        # create father
        self.father = Father(self.cWriter, self.cManager, self.cReader)

        # create messager
        self.messager = Messager(self.father)

        # inputs
        self.accept('escape', self.debug)

        # try to connect
        self.connect()

    def debug(self):
        # testing_alert = Alert(-1)
        # self.father.set_active_level(NIGHT)
        return


app = Client()
app.run()
