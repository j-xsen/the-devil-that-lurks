from direct.directnotify.DirectNotifyGlobal import directNotify


class Game:
    notify = directNotify.newCategory("game")

    def __init__(self, open_to_public=1):
        self.notify.info("Creating game...")

        # allow it to be found?
        self.open = open_to_public

        # array of players for game-wide messaging
        self.players = []

    def add_player(self, connection):
        # make sure player not already in game
        s = set(self.players)
        if connection in s:
            self.notify.info("Player is already in this game")
        else:
            self.notify.info("Adding player to game")
            self.players.append(connection)
