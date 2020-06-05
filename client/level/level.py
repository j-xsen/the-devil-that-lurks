from panda3d.core import VirtualFileSystem
from panda3d.core import Multifile
from panda3d.core import Filename


class Level:
    def __init__(self, name, father):
        self.vfs = VirtualFileSystem.getGlobalPtr()
        self.vfs.mount(Filename("images.mf"), ".", VirtualFileSystem.MFReadOnly)
        self.vfs.mount(Filename("models.mf"), ".", VirtualFileSystem.MFReadOnly)
        self.name = name
        self.father = father
        self.actors = []
        self.lights = []
        self.sprites = loader.loadModel("img/egg/mainmenu.egg")
        self.buttons = []
        self.images = []
        self.text_nodepaths = []
        self.text = []
        self.timer = None

    def create(self):
        # create actors
        # create models
        # create uis
        return

    def destroy(self):
        # delete actors
        # delete models
        # delete uis

        for a in self.actors:
            self.destroy_actor(a)
        self.actors = []

        for l in self.lights:
            self.destroy_light(l)
        self.lights = []

        for b in self.buttons:
            self.destroy_button(b)
        self.buttons = []

        for i in self.images:
            self.destroy_image(i)
        self.images = []

        for t in self.text_nodepaths:
            self.destroy_text_nodepaths(t)
        self.text_nodepaths = []

        for t in self.text:
            self.destroy_text(t)
        self.text = []

        if self.timer:
            self.timer.annihilate()
            self.timer = None

        return

    def destroy_actor(self, a):
        a.cleanup()

    def destroy_light(self, l):
        l.removeNode()

    def destroy_button(self, b):
        b.destroy()

    def destroy_image(self, i):
        i.destroy()

    def destroy_text_nodepaths(self, t):
        t.removeNode()

    def destroy_text(self, t):
        t.destroy()

    def update(self):
        return
