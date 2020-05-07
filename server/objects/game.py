from direct.directnotify.DirectNotifyGlobal import directNotify
from communicator import *
from objects.player import Player
from direct.showbase.RandomNumGen import RandomNumGen
import time
from direct.task.TaskManagerGlobal import taskMgr, Task


class Game:
    notify = directNotify.newCategory("game")

    def __init__(self, _gid, _cwriter, open_to_public=1):
        self.notify.info("Creating game...")

        self.cWriter = _cwriter
        self.gid = _gid
        self.open = open_to_public
        self.started = False
        self.day = True
        self.day_count = 0
        self.red_room = None
        self.killer = None
        self.players = []

    def add_player(self, connection, pid):
        self.notify.debug("Adding player to game")
        p = Player(connection, pid)
        self.players.append(p)
        for p in self.players:
            self.cWriter.send(dg_update_player_count(self.get_player_count()), p.get_connection())

    def remove_player(self, pid):
        self.notify.debug("Removing player {} from game {}".format(pid, self.gid))
        self.players.remove(self.get_player_from_pid(pid))

    def get_player_from_pid(self, pid):
        for p in self.players:
            if p.get_pid() == pid:
                return p
        return False

    def get_gid(self):
        return self.gid

    def vote_to_start(self, pid):
        if not self.started:
            p = self.get_player_from_pid(pid)
            if p:
                p.set_voted_to_start(True)

                vote_count = self.get_vote_count()
                player_count = self.get_player_count()

                if vote_count / player_count >= 0.75:
                    self.notify.debug("Vote start passed! Start game")
                    self.start_game()
                else:
                    self.message_all_players(dg_update_vote_count(vote_count))
            else:
                self.notify.warning("No player w/ that pid")
        else:
            self.notify.warning("Vote to start from {} after game's already started".format(pid))

    def get_player_count(self):
        return len(self.players)

    def get_vote_count(self):
        count = 0
        for p in self.players:
            if p.get_voted_to_start():
                count += 1

        return count

    def set_player_room(self, pid, room):
        # make sure it's day
        if self.day:
            # set their room
            self.get_player_from_pid(pid).set_room(room)
            self.notify.info("Set {} room to {}".format(pid, room))
        else:
            self.notify.warning("{} tried to set room during night".format(pid))

    def start_game(self):
        self.notify.debug("Starting game: {}".format(self.gid))

        # set variables
        self.started = True
        self.day_count = 1

        # tell players
        self.message_all_players(dg_start_game())

        # create task to change time of day
        taskMgr.doMethodLater(TIME, self.change_time, 'Change day/night cycle')

    def change_time(self, taskdata):
        self.notify.debug("Changing time")

        # set vars
        self.day = not self.day
        self.day_count += 1

        # tell players
        self.message_all_players(dg_change_time(self))

        # TODO
        #   check if game has ended
        return Task.again

    def message_all_players(self, dg):
        for p in self.players:
            self.cWriter.send(dg, p.get_connection())
