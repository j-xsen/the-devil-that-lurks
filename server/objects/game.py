from direct.directnotify.DirectNotifyGlobal import directNotify
from communicator import *
from objects.player import Player
from objects.ai import AI
from direct.task.TaskManagerGlobal import taskMgr, Task
from codes import MAX_PLAYERS


class Game:
    notify = directNotify.newCategory("game")

    def __init__(self, _gid, _cwriter, _on_delete, open_to_public=1):
        self.notify.debug("Creating game {}".format(_gid))

        self.cWriter = _cwriter
        self.gid = _gid
        self.on_delete = _on_delete
        self.open = open_to_public
        self.started = False
        self.day = True
        self.day_count = 0
        self.red_room = None
        self.killer = None
        self.players = []

    def delete_this_game(self):
        # end tasks
        taskMgr.remove("DayNight Cycle {}".format(self.gid))

        # tell clients
        self.message_all_players(dg_kick_from_game(GAME_DELETED))

        self.on_delete(self.gid)

    def add_player(self, connection, pid):
        self.notify.debug("Adding player to game")

        p = Player(self.generate_local_id(), _connection=connection, _pid=pid)
        self.players.append(p)
        for p in self.players:
            self.cWriter.send(dg_update_player_count(self.get_player_count()), p.get_connection())

    def remove_player(self, pid):
        self.notify.debug("Removing player {} from game {}".format(pid, self.gid))
        self.players.remove(self.get_player_from_pid(pid))

        # check if any real players left
        if not self.any_real_players():
            self.delete_this_game()

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
        self.notify.info("Starting game: {}".format(self.gid))

        # set variables
        self.started = True
        self.day_count = 1

        # create AI
        while self.get_player_count() < MAX_PLAYERS:
            new_ai = AI(self.generate_local_id())
            self.players.append(new_ai)

        # tell players
        self.message_all_players(dg_start_game())

        # create task to change time of day
        taskMgr.doMethodLater(TIME, self.change_time, "DayNight Cycle {}".format(self.gid))

    def generate_local_id(self):
        local_id = len(self.players)

        # if first player, don't do this
        if len(self.players) != 0:
            while self.get_player_from_local_id(local_id):
                local_id += 1

        return local_id

    def get_player_from_local_id(self, local_id):
        for p in self.players:
            if p.get_local_id == local_id:
                return p
        return False

    def change_time(self, taskdata):
        self.notify.debug("Changing time")

        # set vars
        self.day = not self.day
        if self.day:
            # only change day count when it becomes day
            self.day_count += 1

        if not self.any_real_players():
            self.notify.debug("No non-ai players in game {}".format(self.gid))
            self.delete_this_game()
            return Task.done

        if self.day and self.day_count > MAX_DAYS:
            self.notify.debug("Maximum day_count reached: {}/{}".format(self.day_count, MAX_DAYS))
            self.delete_this_game()
            return Task.done

        # tell players
        self.message_all_players(dg_change_time(self))

        return Task.again

    def any_real_players(self):
        any_real = False
        for p in self.players:
            if not p.ai:
                any_real = True
                break
        return any_real

    def message_all_players(self, dg):
        for p in self.players:
            if not p.ai:
                self.cWriter.send(dg, p.get_connection())
