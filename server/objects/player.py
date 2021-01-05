import random
from communications.codes import ROOMS
from names import NAMES


class Player:
    def __init__(self, local_id, pid=None, ai=False):
        self.voted_to_start = False
        self.room = None
        self.blocking = None
        self.pid = pid
        self.alive = True
        self.ai = ai
        self.local_id = local_id
        self.name = "???"
        self.wants_to_kill = False

    def __repr__(self):
        return f"Player({self.pid})[{self.local_id}]"

    def random_name(self):
        self.name = random.choice(NAMES)

    def random_room(self):
        self.room = random.choice(ROOMS)
