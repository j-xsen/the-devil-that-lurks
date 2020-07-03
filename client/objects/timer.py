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
        self.interval = None

        self.types[style](self)

    def create_sun(self):
        """
        Creates the sun timer
        """

        # load image
        self.img = OnscreenImage(image=self.egg.find('**/sun'), pos=(1.15, 0, 0.75),
                                 color=(255, 255, 0, 1), scale=0.25)

        # interval
        self.interval = LerpFunc(self.run_interval, fromData=1, toData=0, duration=TIME)
        self.interval.start()

        return

    def create_moon(self):
        """
        Creates the moon timer
        """

        # load image
        self.img = OnscreenImage(image=self.egg.find('**/moon-quarter'), pos=(0, 0, 0),
                                 color=(1, 1, 1, 1), scale=0.25)

        # interval
        self.interval = LerpFunc(self.run_interval, fromData=1, toData=0, duration=TIME)
        self.interval.start()

        return

    def create_gun(self):
        """
        Creates the gun timer
        """

        # load image
        self.img = OnscreenImage(image=self.egg.find('**/gun-0'), pos=(1.05, 0, 0.75), scale=0.25)

        # interval
        self.interval = LerpFunc(self.run_interval, fromData=1, toData=0, duration=TIME)
        self.interval.start()

        return

    def run_interval(self, c):
        if self.style == SUN:
            self.img.setColor((1, c, 0, 1))
            self.img.setPos(1.15-(c/4), 0, 0.75+(math.sin(math.pi*c)/10))
        elif self.style == MOON:
            self.img.setColor((1, c, c, 1))
            self.img.setPos(0.9+(c/4), 0, 0.75+(math.sin(math.pi*c)/10))
        elif self.style == GUN:
            self.img.setHpr(0, 0, 360*(1-c)-60)

            if c % (1 / 6) < 0.05:
                if c % (1 / 6) > 0.025:
                    self.img.setColor((1, 40*(c % (1 / 6)), 40*(c % (1 / 6)), 1))
                else:
                    self.img.setImage(self.egg.find('**/gun-{}'.format(6 - (round(c / (1 / 6))))))
                    self.img.setColor((1, 1-40*(c % (1 / 6)), 1-40*(c % (1 / 6)), 1))
            else:
                self.img.setColor((1, 1, 1, 1))

    def annihilate(self):
        self.interval.finish()
        self.img.destroy()
        loader.unloadModel(self.egg)
        VirtualFileSystem.getGlobalPtr().unmount("mf/timer.mf")
        del self

    types = {
        SUN: create_sun,
        MOON: create_moon,
        GUN: create_gun
    }
