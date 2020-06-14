from direct.directnotify.DirectNotifyGlobal import directNotify
from datagrams import *
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

        p = Player(self.generate_local_id(), _connection=connection, _pid=pid)
        self.players.append(p)
        self.message_all_players(dg_add_player(p.get_local_id()))

        # send all players to the new player
        for existing in self.players:
            if existing != p:
                self.message_player(dg_update_player_name(existing.get_local_id(), existing.get_name()),
                                    p.get_local_id())

    def remove_player(self, pid):
        self.remove_player_from_local_id(self.get_local_id_from_pid(pid))

    def remove_player_from_local_id(self, local_id):
        self.notify.debug("Removing player {} from game {}".format(local_id, self.gid))

        # needs to be done before they're removed bc we use their data
        if self.started:
            self.message_all_players(dg_has_died(local_id))
        else:
            self.message_all_players(dg_remove_player(local_id))

        self.players.remove(self.get_player_from_local_id(local_id))

        if not self.any_real_players():
            self.delete_this_game()

        if not self.started:
            self.verify_vote_to_start()

    def set_name(self, pid, name):
        # TODO validate name
        self.notify.debug("changing name to {}".format(name))
        self.get_player_from_pid(pid).set_name(name)

        # tell players
        self.message_all_players(dg_update_player_name(self.get_local_id_from_pid(pid), name))

    def get_gid(self):
        return self.gid

    def vote_to_start(self, pid):
        if not self.started:
            p = self.get_player_from_pid(pid)
            if p:
                p.set_voted_to_start(True)

                self.verify_vote_to_start()
            else:
                self.notify.warning("No player w/ that pid")
        else:
            self.notify.warning("Vote to start from {} after game's already started".format(pid))

    def verify_vote_to_start(self):
        """
        Called to verify if the game should start. Should be called when players leave lobbys or cast
        their vote.
        :return: if the vote passes
        :rtype: bool
        """
        vote_count = self.get_vote_count()
        player_count = self.get_player_count()

        if vote_count / player_count >= 0.75:
            self.notify.debug("Vote start passed! Start game!")
            self.start_game()
        else:
            self.message_all_players(dg_update_vote_count(vote_count))

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
    def get_players_in_room(self, room, include_killer):
        in_room = []
        for p in self.players:
            if include_killer:
                if p.get_room() == room:
                    in_room.append(p.get_local_id())
            else:
                if p.get_room() == room and p.get_local_id() != self.killer:
                    in_room.append(p.get_local_id())
        return in_room

    def start_game(self):
        self.notify.info("Starting game: {}".format(self.gid))

        # set variables
        self.started = True
        self.day_count = 1

        # fix people who haven't updated their name
        for p in self.players:
            if p.get_name() == "???":
                p.set_random_name()

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
            player = self.get_player_from_pid(pid)
            player.wants_to_kill = choice
        else:
            self.notify.warning("player {} tried to set kill, but they're not the killer".format(pid))

    def generate_local_id(self):
        local_id = 0
        while local_id in self.get_local_id_pool():
            local_id += 1
            if local_id >= 255:
                # i'd hope it'd never get it but just in case i guess
                self.notify.error("Too high!")
                break

        return local_id

    def get_local_id_pool(self):
        """
        get every currently taken local_id
        :return: list of local_ids
        :rtype: list
        """
        local_ids = []
        for p in self.players:
            local_ids.append(p.get_local_id())
        return local_ids

    def get_player_from_local_id(self, local_id):
        """
        get the player object from local_id
        :param local_id: the player's local_id
        :type local_id: int
        :return: player object or False, if lookup failed
        :rtype: Player
        """
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

    def get_player_from_pid(self, pid):
        for p in self.players:
            if p.get_pid() == pid:
                return p
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

                # send them the amount of people in their room
                self.message_player(dg_how_many_in_room(len(self.get_players_in_room(p.get_room(), True))),
                                    p.get_local_id())

        # kill player if going into day
        if self.day:
            # check if killer wants to kill
            killer = self.get_player_from_local_id(self.killer)
            if killer.get_wants_to_kill():
                # get red_room
                self.red_room = killer.get_room()
                # get all players in that room
                possible_victims = self.get_players_in_room(self.red_room, False)
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
