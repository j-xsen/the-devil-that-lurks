from direct.directnotify.DirectNotifyGlobal import directNotify
from objects.player import Player
from names import NAMES
import random


class AI(Player):
    notify = directNotify.newCategory("ai")

    def __init__(self, _local_id):
        Player.__init__(self, _local_id, random.choice(NAMES), _ai=True)

    def get_connection(self):
        self.notify.warning("Someone request AI's connection...")
        return False

    # this is ran going into night
    def night_run(self):
        # select room
        self.random_room()
