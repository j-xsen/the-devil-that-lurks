from direct.gui.DirectGui import DirectFrame, DirectButton, DGG
from direct.gui.OnscreenText import OnscreenText
from localization.en import LOCAL_EN
from communications.codes import GENERAL
from panda3d.core import VirtualFileSystem, Filename, TextNode
from objects.notifier import Notifier


class Alert(Notifier):
    def __init__(self, reason):
        Notifier.__init__(self, "alert")
        VirtualFileSystem.getGlobalPtr().mount(Filename("mf/alert.mf"), ".", VirtualFileSystem.MFReadOnly)
        ok = loader.loadModel("alert.egg")

        if reason not in LOCAL_EN:
            reason = GENERAL

        self.reason = reason

        self.bg_frame = DirectFrame(frameColor=(0, 0, 0, 0),
                                    frameSize=(-1, 1, -1, 1), suppressMouse=1, state=DGG.NORMAL,
                                    sortOrder=1000)
        self.frame = DirectFrame(frameSize=(1, 1, 1, 1),
                                 image=ok.find('**/alert'),
                                 image_scale=(1, 0, 0.6), state=DGG.NORMAL, parent=self.bg_frame)
        self.text = OnscreenText(text=LOCAL_EN[reason], fg=(1, 1, 1, 1), pos=(0, 0.15, 0),
                                 align=TextNode.ACenter, wordwrap=13, parent=self.frame)
        self.button = DirectButton(geom=(ok.find('**/ok-ready'),
                                         ok.find('**/ok-click'),
                                         ok.find('**/ok-hover'),
                                         ok.find('**/ok-click')),
                                   relief=None, geom_scale=(0.3, 0, 0.15), geom_pos=(0, 0, -0.175),
                                   pressEffect=0, command=self.destroy, parent=self.frame)

        self.notify.debug(f"[__init__] Created Alert with reason {self.reason}")

        loader.unloadModel(ok)

    def __repr__(self):
        return str(self.reason)

    def destroy(self):
        VirtualFileSystem.getGlobalPtr().unmount("mf/alert.mf")
        VirtualFileSystem.getGlobalPtr().unmount("mf/ok_small.mf")
        self.bg_frame.destroy()
        self.frame.destroy()
        self.button.destroy()
        self.text.cleanup()
        self.text.destroy()
        del self.frame
        del self.button
        del self.text
        del self
