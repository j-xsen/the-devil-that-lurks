from direct.directnotify.DirectNotifyGlobal import directNotify
from communications.datagrams import *
from objects.player import Player
from objects.ai import AI
from direct.task.TaskManagerGlobal import taskMgr, Task
from communications.codes import MAX_PLAYERS
import random


class Game:
    notify = directNotify.newCategory("game")

    def __init__(self, gid, msgr, open_to_public=1):
        self.notify.debug("Creating game {}".format(gid))

        self.gid = gid
        self.msgr = msgr
        self.open = open_to_public
        self.started = False
        self.day = True
        self.day_count = 0
        self.red_room = 0
        self.killer = None
        self.players = []

    """
    # MESSAGING
    """

    def message_player(self, dg, local_id):
        """
        Sends a message to a player based off their Local ID
        :param dg: Datagram to send
        :type dg: PyDatagram
        :param local_id: The player's local ID
        :type local_id: int
        :return: if successful
        :rtype: bool
        """
        p = self.get_player(local_id=local_id)

        if not p.get_ai():
            return self.msgr.send_message(p.get_pid(), dg)

        return False

    def message_all_players(self, dg):
        """
        Sends a message to every player
        :param dg: the datagram you want to send
        :type dg: PyDatagram
        :return: if successful
        :rtype: bool
        """
        for p in self.players:
            if not p.ai:
                if not self.message_player(dg, p.get_local_id()):
                    return False
        return True

    def message_killer(self, dg):
        """
        Sends a message to the killer
        :param dg: the datagram you want to send
        :type dg: PyDatagram
        :return: if successful
        :rtype: bool
        """
        return self.message_player(dg, self.killer)

    """
    # PLAYER RETRIEVAL
    """

    def get_pid_from_local_id(self, local_id):
        """
        Get the PID from the Local ID
        :param local_id: the player's local ID
        :type local_id: int
        :return: player object, if found
        :rtype: Player
        """
        for p in self.players:
            if p.get_local_id() == local_id:
                return p.get_pid()
        return False

    def get_local_id_from_pid(self, pid):
        """
        Gets a player's Local ID from their PID
        :param pid: the player's PID
        :type pid: int
        :return: the player's local ID
        :rtype: int
        """
        for p in self.players:
            if p.get_pid() == pid:
                return p.get_local_id()
        return False

    def get_player(self, pid=-1, local_id=-1):
        """
        Gets Player object from Player ID
        :param pid: the player's  PID
        :type pid: int
        :param local_id: the player's local ID
        :type local_id: int
        :return: the Player object of the player, if found
        :rtype: Player
        """
        if local_id < 0:
            if pid < 0:
                self.notify.warning("get_player w/ no pid nor local_id")
                return False
            local_id = self.get_local_id_from_pid(pid)

        for p in self.players:
            if p.get_local_id() == local_id:
                return p
        return False

    """
    # PLAYER RELATED
    """

    def generate_local_id(self):
        """
        :return: an available local_id
        :rtype: int
        """
        local_id = 0
        while local_id in self.get_local_id_pool():
            local_id += 1
            if local_id >= 255:
                # i'd hope it'd never get it but just in case i guess
                self.notify.error("Too high!")
                break

        return local_id

    def add_player(self, pid):
        """
        Adds a player using the player's ID
        :param pid: The Player ID you want to add
        :type pid: int
        :return: if successful
        :rtype: bool
        """
        self.notify.debug("Adding player to game")

        p = Player(self.generate_local_id(), pid=pid)
        self.players.append(p)
        self.message_all_players(dg_add_player(p.get_local_id()))

        # send all players to the new player
        for existing in self.players:
            if existing != p:
                self.message_player(dg_update_player_name(existing.get_local_id(), existing.get_name()),
                                    p.get_local_id())

        return True

    def remove_player(self, local_id=-1, pid=-1):
        """
        Removes player using their Local ID
        :param local_id: the palyer's local ID
        :type local_id: int
        :param pid: the player's PID
        :type pid: int
        :return: if successful
        :rtype: bool
        """
        if local_id < 0:
            if pid < 0:
                self.notify.warning("remove_player called w/ no local_id nor pid")
                return False

            local_id = self.get_local_id_from_pid(pid)

        self.notify.debug("Removing player {} from game {}".format(local_id, self.gid))

        # needs to be done before they're removed bc we use their data
        if self.started:
            self.message_all_players(dg_has_died(local_id))
        else:
            self.message_all_players(dg_remove_player(local_id))

        self.players.remove(self.get_player(local_id=local_id))

        if not self.any_real_players():
            self.delete_this_game()
            return True

        if not self.started:
            self.verify_vote_to_start()

        return True

    def set_name(self, pid, name):
        """
        Set the player with this PID's name
        :param pid: the player's PID
        :type pid: int
        :param name: the new name
        :type name: string
        :return: if successful
        :rtype: bool
        """
        # TODO validate name
        self.notify.debug("changing name to {}".format(name))
        self.get_player(pid=pid).set_name(name)

        # tell players
        return self.message_all_players(dg_update_player_name(self.get_local_id_from_pid(pid), name))

    def vote_to_start(self, pid):
        """
        Set the player's Vote to Start status
        :param pid:
        :type pid:
        :return:
        :rtype:
        """
        if not self.started:
            p = self.get_player(pid=pid)
            if p:
                p.set_voted_to_start(True)

                self.verify_vote_to_start()
            else:
                self.notify.warning("No player w/ that pid")
        else:
            self.notify.warning("Vote to start from {} after game's already started".format(pid))

    def set_player_room(self, pid, room):
        """
        Set the desired room for a player
        :param pid: the player's PID
        :type pid: int
        :param room: the room that they desire
        :type room: int
        :return: if successful
        :rtype: bool
        """
        # make sure it's day
        if self.day:
            # set their room
            self.get_player(pid=pid).set_room(room)
            self.notify.info("Set {} room to {}".format(pid, room))
            return True
        else:
            self.notify.warning("{} tried to set room during night".format(pid))
            return False

    def set_kill_choice(self, pid, choice):
        """
        Set if the killer wants to kill or not
        :param pid: the player's PID
        :type pid: int
        :param choice: Do they want to kill?
        :type choice: bool
        :return: if successful
        :rtype: bool
        """
        if self.killer == self.get_local_id_from_pid(pid):
            player = self.get_player(pid=pid)
            player.set_wants_to_kill(choice)
            return True
        else:
            self.notify.warning("player {} tried to set kill, but they're not the killer".format(pid))
            return False

    """
    # DATA RETRIEVAL
    """

    def get_gid(self):
        return self.gid

    def get_player_count(self):
        return len(self.players)

    def get_vote_count(self):
        """
        Finds out how many players have voted to start the game
        :return: Number of players who have Voted to Start
        :rtype: int
        """
        count = 0
        for p in self.players:
            if p.get_voted_to_start():
                count += 1
        return count

    def get_players_in_room(self, room, include_killer):
        """
        Gets a list of players' local IDs in a room
        :param room: the room to search
        :type room: int
        :param include_killer: should we include the killer in this search?
        :type include_killer: bool
        :return: the list of players' local IDs in a room
        :rtype: list
        """
        in_room = []
        for p in self.players:
            if include_killer:
                if p.get_room() == room:
                    in_room.append(p.get_local_id())
            else:
                if p.get_room() == room and p.get_local_id() != self.killer:
                    in_room.append(p.get_local_id())
        return in_room

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

    def any_real_players(self):
        """
        Checks if there's any real players left in the game
        :return: if there's any real players left in the game
        :rtype: bool
        """
        for p in self.players:
            if not p.ai:
                return True
        return False

    def check_if_available(self):
        """
        Checks requirements for a game to be available to join
        :return: if available
        :rtype: bool
        """
        return self.open and not self.started

    def verify_vote_to_start(self):
        """
        Called to verify if the game should start. Should be called when players leave lobbies or cast
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

    """
    # GAME FUNCTIONS
    """

    def start_game(self):
        """
        Called upon the game starting for the first time
        """
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

        # tell players
        self.message_all_players(dg_start_game(self))

        # tell killer
        self.message_killer(dg_you_are_killer())

        # create task to change time of day
        taskMgr.doMethodLater(TIME, self.change_time, "DayNight Cycle {}".format(self.gid))

    def change_time(self, taskdata):
        # set vars
        self.day = not self.day
        if self.day:
            # only change day count when it becomes day
            self.day_count += 1

            # check if changing day count put us over the limit
            if self.day_count > MAX_DAYS:
                self.notify.debug("Maximum day_count reached: {}/{}".format(self.day_count, MAX_DAYS))
                self.delete_this_game()
                return Task.done

            # check if killer wants to kill
            killer = self.get_player(local_id=self.killer)
            if killer.get_wants_to_kill():
                # KILL
                self.red_room = killer.get_room()
                possible_victims = self.get_players_in_room(self.red_room, False)
                if len(possible_victims) > 0:
                    # select random
                    victim = random.choice(possible_victims)

                    self.notify.debug("Killing {} in {}".format(victim, self.gid))

                    if self.get_player(local_id=victim).ai:
                        self.remove_player(local_id=victim)
                    else:
                        self.msgr.remove_player_from_game(self.get_pid_from_local_id(victim), KILLED)

                        # check if need to end game due to lack of players
                        if not self.any_real_players():
                            self.notify.debug("No non-ai players in game {}".format(self.gid))
                            self.delete_this_game()
                            return Task.done
                else:
                    self.red_room = 0
                    self.message_killer(dg_kill_failed_empty_room())
            else:
                # killer doesn't want to kill
                self.red_room = 0

            # reset player rooms
            for p in self.players:
                p.set_room(None)

            # reset killer's choice
            killer.set_wants_to_kill(False)
        else:
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

        # tell players
        if self.day:
            self.message_all_players(dg_goto_day(self))
        else:
            self.message_all_players(dg_goto_night(self))

        return Task.again

    def delete_this_game(self):
        # end tasks
        taskMgr.remove("DayNight Cycle {}".format(self.gid))

        # tell clients
        self.message_all_players(dg_kick_from_game(GAME_DELETED))

        # tell msgr to delete this game
        self.msgr.delete_game(self.gid)
