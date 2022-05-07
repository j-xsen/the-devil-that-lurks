from direct.directnotify.DirectNotifyGlobal import directNotify
from panda3d.core import VirtualFileSystem, Multifile
from panda3d.core import Filename


class Level:
    def __init__(self, name, multifiles, level_holder):
        # notify
        self.notify = directNotify.newCategory("level")
        self.vfs = VirtualFileSystem.getGlobalPtr()
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
        self.clickables = {}
        self.timer = None

    def __repr__(self):
        return f"Level({self.name})"

    def create_clickable(self, name, clickable):
        self.clickables[name] = clickable
        self.accept(f"mouse_ray-in-{name}", clickable.collision)
        self.accept(f"{name}-in-mouse_ray", clickable.collision)

    def create(self):
        self.multifiles = Multifile()
        self.multifiles.openReadWrite("mf/art.mf")

        if self.vfs.mount(self.multifiles, ".", VirtualFileSystem.MFReadOnly):
            self.notify.info("[create] mounted mf/art.mf!")

    def destroy(self):
        self.notify.debug(f"[destroy] destroying {self.name}")
        # delete actors
        # delete models
        # delete uis

        for a in self.actors:
            self.actors[a].cleanup()
        self.actors = {}

        for c in self.clickables:
            self.clickables[c].cleanup()
        self.clickables = {}

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

        if type(self.multifiles) == list:
            for f in self.multifiles:
                self.level_holder.vfs.unmount(f)
                self.notify.warning(f"[destroy] (for) unmounted mf/{self.name}.mf")
        else:
            self.level_holder.vfs.unmount(self.multifiles)

        return
