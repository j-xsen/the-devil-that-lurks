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

    def get_pid(self):
        """
        Gets the player's PID.
        This is used because this number is associated with their connection, meaning you need this
            to send messages.
        :return: Player ID
        :rtype: int
        """
        return self.pid

    def get_local_id(self):
        """
        Get the player's Local ID
        :return: Local ID
        :rtype: int
        """
        return self.local_id

    # self.name
    def set_name(self, name):
        self.name = name

    def set_random_name(self):
        self.name = random.choice(NAMES)

    def get_name(self):
        return self.name

    # self.wants_to_kill
    def set_wants_to_kill(self, want):
        self.wants_to_kill = want

    def get_wants_to_kill(self):
        return self.wants_to_kill

    # self.voted_to_start
    def set_voted_to_start(self, _voted_to_start):
        self.voted_to_start = _voted_to_start

    def get_voted_to_start(self):
        return self.voted_to_start

    # self.room
    def set_room(self, _room):
        self.room = _room

    def get_room(self):
        return self.room

    def random_room(self):
        self.room = random.choice(ROOMS)

    # self.blocking
    def set_block(self, _blocking):
        self.blocking = _blocking

    def get_block(self):
        return self.blocking

    # self.alive
    def set_alive(self, _alive):
        self.alive = _alive

    def get_alive(self):
        return self.alive

    # self.ai
    def get_ai(self):
        return self.ai
