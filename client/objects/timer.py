from direct.gui.OnscreenImage import OnscreenImage
from panda3d.core import VirtualFileSystem, Filename, TextNode
from direct.interval.LerpInterval import LerpColorInterval, LerpFunc
import math
from communications.codes import TIME

SUN = 0
MOON = 1
GUN = 2


class Timer:

    def __init__(self, style):
        """
        Timer class with fun pictures
        @param style: 0 = SUN, 1 = MOON, 2 = GUN
        @type style: int
        """
        self.style = style
        VirtualFileSystem.getGlobalPtr().mount(Filename("mf/timer.mf"), ".", VirtualFileSystem.MFReadOnly)
        self.egg = loader.loadModel("timer.egg")
        self.img = None

        self.types[style](self)

    def create_sun(self):
        """
        Creates the sun timer
        """

        # load image
        self.img = OnscreenImage(image=self.egg.find('**/sun'), pos=(0.75, 0, 0.75),
                                     color=(255, 255, 0, 1), scale=0.25)

        # interval

        self.intrvl_sun = LerpFunc(self.set_color, fromData=1, toData=0, duration=TIME)
        self.intrvl_sun.start()

        return

    def set_color(self, c):
        self.img.setColor((1, c, 0, 1))
        self.img.setPos(1.15-(c/4), 0, 0.75+(math.sin(math.pi*c)/10))

    def create_moon(self):
        """
        Creates the moon timer
        """
        return

    def create_gun(self):
        """
        Creates the gun timer
        """
        return

    def annihilate(self):
        self.intrvl_sun.finish()
        self.img.destroy()
        loader.unloadModel(self.egg)
        VirtualFileSystem.getGlobalPtr().unmount("mf/timer.mf")
        del self

    types = {
        SUN: create_sun,
        MOON: create_moon,
        GUN: create_gun
    }
