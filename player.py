class Player:
    def __init__(self, number, name, ui, local_player):
        self.name = name
        self.number = number
        self.ui = ui
        self.local_player = local_player
        self.room = "Living Room"

        self.suspicion = [0, 0, 0, 0, 0, 0, 0, 0]
