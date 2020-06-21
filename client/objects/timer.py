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

        self.model = loader.loadModel("timer.egg")

        self.types[style](self)

    def create_sun(self):
        """
        Creates the sun timer
        """
        return

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

    types = {
        SUN: create_sun,
        MOON: create_moon,
        GUN: create_gun
    }
