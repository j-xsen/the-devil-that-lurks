class Player:
    def __init__(self, number, name, ui, local_player):
        self.name = name
        self.number = number
        self.ui = ui
        self.local_player = local_player
        self.room = "Living Room"
        self.suspicion = [10, 10, 10, 10, 10, 10, 10, 10]
        self.status = "Living"

        self.pos = (0, 0, 0)

        self.socialness = 0

        # Batteries are used to shine a light on one other play
        self.batteries = 3

    def get_number(self):
        return self.number

    def get_name(self):
        return self.name

    def set_pos(self, pos):
        self.pos = pos

    def get_pos(self):
        return self.pos