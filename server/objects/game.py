from direct.directnotify.DirectNotifyGlobal import directNotify
from communicator import *
from objects.player import Player
from objects.ai import AI
from direct.task.TaskManagerGlobal import taskMgr, Task
from codes import MAX_PLAYERS
import random


class Game:
    notify = directNotify.newCategory("game")

    def __init__(self, _gid, _cwriter, _on_delete, _on_remove_player, open_to_public=1):
        self.notify.debug("Creating game {}".format(_gid))

        self.cWriter = _cwriter
        self.gid = _gid
        self.on_delete = _on_delete
        self.on_remove_player = _on_remove_player
        self.open = open_to_public
        self.started = False
        self.day = True
        self.day_count = 0
        self.red_room = 0
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

        p = Player(self.generate_local_id(), "jaxsen", _connection=connection, _pid=pid)
        self.players.append(p)
        self.message_all_players(dg_update_player_count(self.get_player_count()))

    def remove_player(self, pid):
        self.notify.debug("Removing player {} from game {}".format(pid, self.gid))
        self.players.remove(self.get_player_from_pid(pid))

        # check if any real players left
        if not self.any_real_players():
            self.delete_this_game()

        # tell all players new player count
        self.message_all_players(dg_update_player_count(self.get_player_count()))

        if not self.started:
            self.message_all_players(dg_update_vote_count(self.get_vote_count()))

    def remove_player_from_local_id(self, local_id):
        self.notify.debug("Removing player {} from game {}".format(local_id, self.gid))
        self.players.remove(self.get_player_from_local_id(local_id))

        if not self.any_real_players():
            self.delete_this_game()

        if not self.started:
            self.message_all_players(dg_update_player_count(self.get_player_count()))
            self.message_all_players(dg_update_vote_count(self.get_vote_count()))
        else:
            # TODO
            #   tell players to mark left as dead
            self.notify.debug("Removed player from game")

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

    # returns array of local_ids of NOT the killers
    def get_players_in_room(self, room):
        in_room = []
        for p in self.players:
            if p.get_room() == room and p.get_local_id() != self.killer:
                in_room.append(p.get_local_id())
        return in_room

    def start_game(self):
        self.notify.info("Starting game: {}".format(self.gid))

        # set variables
        self.started = True
        self.day_count = 1

        # create AI
        while self.get_player_count() < MAX_PLAYERS:
            new_ai = AI(self.generate_local_id())
            self.players.append(new_ai)

        # assign killer
        # TODO
        #   make it random and not just the first player - but i need to debug
        self.killer = self.players[0].get_local_id()
        self.notify.debug("Killer: {}".format(self.killer))

        # tell players
        self.message_all_players(dg_start_game(self))

        # tell killer
        self.message_killer(dg_you_are_killer())

        # create task to change time of day
        taskMgr.doMethodLater(TIME, self.change_time, "DayNight Cycle {}".format(self.gid))

    def set_kill_choice(self, pid, choice):
        if self.killer == self.get_local_id_from_pid(pid):
            self.get_player_from_pid(pid).set_wants_to_kill(choice)
        else:
            self.notify.warning("player {} tried to set kill, but they're not the killer".format(pid))

    def generate_local_id(self):
        local_id = len(self.players)

        # if first player, don't do this
        if len(self.players) != 0:
            while self.get_player_from_local_id(local_id):
                local_id += 1

        return local_id

    def get_player_from_local_id(self, local_id):
        for p in self.players:
            if p.get_local_id() == local_id:
                return p
        return False

    def get_pid_from_local_id(self, local_id):
        for p in self.players:
            if p.get_local_id() == local_id:
                self.notify.debug("{} does match {}".format(p.get_local_id(), local_id))
                return p.get_pid()
            else:
                self.notify.debug("{} does not match {}".format(p.get_local_id(), local_id))
        return False

    def get_local_id_from_pid(self, pid):
        for p in self.players:
            if p.get_pid() == pid:
                return p.get_local_id()
        return False

    def change_time(self, taskdata):
        # set vars
        self.day = not self.day
        if self.day:
            # only change day count when it becomes day
            self.day_count += 1
        else:
            # it's going into night

            # remove killer's choice bc it defaults at No
            self.get_player_from_local_id(self.killer).set_wants_to_kill = False

            for p in self.players:
                # run ai
                if p.ai:
                    p.night_run()
                else:
                    # make sure every one's picked a room, if they haven't give them a random one
                    if not p.get_room():
                        p.random_room()

        # kill player if going into day
        if self.day:
            # check if killer wants to kill
            killer = self.get_player_from_local_id(self.killer)
            if killer.get_wants_to_kill():
                # get red_room
                self.red_room = killer.get_room()
                # get all players in that room
                possible_victims = self.get_players_in_room(self.red_room)
                if len(possible_victims) > 0:
                    # select random
                    victim = random.choice(possible_victims)

                    self.notify.debug("Killing {} in {}".format(victim, self.gid))

                    to_remove = self.get_player_from_local_id(victim)
                    if to_remove.ai:
                        self.remove_player_from_local_id(victim)
                    else:
                        self.on_remove_player(self.get_pid_from_local_id(victim), KILLED)
                else:
                    self.red_room = 0
                    self.message_killer(dg_kill_failed_empty_room())
            else:
                # killer doesn't want to kill
                self.red_room = 0

        # check if need to end game
        if not self.any_real_players():
            self.notify.debug("No non-ai players in game {}".format(self.gid))
            self.delete_this_game()
            return Task.done

        if self.day and self.day_count > MAX_DAYS:
            self.notify.debug("Maximum day_count reached: {}/{}".format(self.day_count, MAX_DAYS))
            self.delete_this_game()
            return Task.done

        # tell players
        if self.day:
            self.message_all_players(dg_goto_day(self))
        else:
            self.message_all_players(dg_goto_night(self))

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
                self.message_player(dg, p.get_local_id())

    def message_player(self, dg, local_id):
        p = self.get_player_from_local_id(local_id)
        if not p.ai:
            self.cWriter.send(dg, p.get_connection())

    def message_killer(self, dg):
        self.message_player(dg, self.killer)
