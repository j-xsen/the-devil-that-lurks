from direct.gui.DirectGui import DirectCheckButton
from panda3d.core import VirtualFileSystem, Filename


class Checkbox:
    def __init__(self, scale, position, function, default=0):
        VirtualFileSystem.getGlobalPtr().mount(Filename("mf/checkbox.mf"), ".", VirtualFileSystem.MFReadOnly)

        self.egg = loader.loadModel("checkbox/checkbox.egg")
        box_image = (self.egg.find("**/check-empty"), self.egg.find("**/check-checked"), None)
        self.button = DirectCheckButton(boxImage=box_image, boxRelief=None, relief=None,
                                        command=function, scale=scale, pos=position)

    def destroy(self):
        VirtualFileSystem.getGlobalPtr().unmount("mf/checkbox.mf")
        loader.unloadModel(self.egg)
