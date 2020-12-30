from panda3d.core import VirtualFileSystem
from panda3d.core import Filename


class Level:
    def __init__(self, name, multifiles, level_holder):
        self.multifiles = multifiles
        self.name = name
        self.level_holder = level_holder
        self.messager = self.level_holder.messager
        self.actors = {}
        self.lights = {}
        self.sprites = None
        self.gui = {}
        self.images = {}
        self.text_nodepaths = {}
        self.text = {}
        self.timer = None

    def create(self):
        for f in self.multifiles:
            self.level_holder.vfs.mount(Filename("mf/{}".format(f)), ".", VirtualFileSystem.MFReadOnly)
        return

    def destroy(self):
        # delete actors
        # delete models
        # delete uis

        for a in self.actors:
            self.actors[a].cleanup()
        self.actors = {}

        for l in self.lights:
            self.lights[l].removeNode()
        self.lights = {}

        for g in self.gui:
            self.gui[g].destroy()
        self.gui = {}

        for i in self.images:
            self.images[i].destroy()
        self.images = {}

        for t in self.text_nodepaths:
            self.text_nodepaths[t].removeNode()
        self.text_nodepaths = {}

        for t in self.text:
            self.text[t].destroy()
        self.text = {}

        if self.timer:
            self.timer.annihilate()
            self.timer = None

        for f in self.multifiles:
            self.level_holder.vfs.unmount(f)

        return
