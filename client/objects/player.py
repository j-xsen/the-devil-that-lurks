"""
Holds all player information
"""


class Player:
    def __init__(self, local_id, name="???"):
        self.local_id = local_id
        self.name = name
        self.alive = True
