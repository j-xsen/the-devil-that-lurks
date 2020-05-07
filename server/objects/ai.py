from direct.directnotify.DirectNotifyGlobal import directNotify
from direct.showbase.RandomNumGen import RandomNumGen
from objects.player import Player
import time


class AI(Player):
    notify = directNotify.newCategory("ai")

    def __init__(self):
        Player.__init__(self, None, RandomNumGen(int(round(time.time() * 1000))).randint(0, 65535), _ai=True)
        self.notify.debug("Creating AI")

    def get_connection(self):
        self.notify.warning("Someone request AI's connection...")
        return False
