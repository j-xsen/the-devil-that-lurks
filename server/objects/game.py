from communications.datagrams import *
from objects.player import Player
from objects.ai import AI
from direct.task.TaskManagerGlobal import taskMgr, Task
from communications.codes import MAX_PLAYERS
import random
from objects.notifier import Notifier


class Game(Notifier):

    def __init__(self, gid, msgr, open_to_public=1):
        Notifier.__init__(self, "game")

        self.gid = gid
        self.msgr = msgr
        self.open = open_to_public
        self.started = False
        self.day = True
        self.day_count = 0
        self.red_room = 0
        self.killer = None
        self.players = []

        self.notify.debug(f"[__init__] Created game {gid}")

    """
    # MESSAGING
    """

    def message_player(self, dg, local_id):
        """
        Sends a message to a player based off their Local ID
        @param dg: Datagram to send
        @type dg: PyDatagram
        @param local_id: The player's local ID
        @type local_id: int
        @return: if successful
        @rtype: bool
        """
        p = self.get_player(local_id=local_id)

        if p:
            if not p.ai:
                return self.msgr.send_message(p.pid, dg)
            else:
                self.notify.warning("[message_player] Attempted to send message to AI")
        else:
            self.notify.warning(f"[message_player] Attempted to send message to a non-existent player {local_id}")

        return False

    def message_all_players(self, dg, exclude=[]):
        """
        @param dg: The datagram to send
        @type dg: PyDatagram
        @param exclude: LocalIDs to exclude
        @type exclude: list
        @return: If successful
        @rtype: bool
        """
        for p in self.players:
            if not p.ai and p.local_id not in exclude:
                if not self.message_player(dg, p.local_id):
                    self.notify.warning(f"[message_all_players] Failed to message {p.local_id} {exclude}!")
                    return False
        return True

    def message_killer(self, dg):
        """
        Sends a message to the killer
        @param dg: the datagram you want to send
        @type dg: PyDatagram
        @return: if successful
        @rtype: bool
        """
        return self.message_player(dg, self.killer)

    """
    # PLAYER RETRIEVAL
    """

    def get_pid_from_local_id(self, local_id):
        """
        Get the PID from the Local ID
        @param local_id: the player's local ID
        @type local_id: int
        @return: player object, if found
        @rtype: Player
        """
        for p in self.players:
            if p.get_local_id() == local_id:
                return p.get_pid()
        return None

    def get_local_id_from_pid(self, pid):
        """
        Gets a player's Local ID from their PID
        @param pid: the player's PID
        @type pid: int
        @return: the player's local ID
        @rtype: int
        """
        if pid is None:
            self.notify.warning(f"[get_local_id_from_pid] Requested to find LocalID from invalid PID {pid}"
                                f" in game {self.gid}")
            return None
        for p in self.players:
            if p.pid == pid:
                self.notify.debug(f"[get_local_id_from_pid] Found LocalID {p.local_id} for player {pid}"
                                  f" in game {self.gid}")
                return p.local_id
        self.notify.warning(f"[get_local_id_from_pid] Failed to find LocalID for player {pid} in game"
                            f" {self.gid}")
        return None

    def get_player(self, pid=None, local_id=None):
        """
        Gets Player object from Player ID
        @param pid: the player's  PID
        @type pid: int
        @param local_id: the player's local ID
        @type local_id: int
        @return: the Player object of the player, or None if not found
        @rtype: Player
        """
        if local_id is None:
            local_id = self.get_local_id_from_pid(pid)
            if local_id is None:
                self.notify.warning(f"[get_player] Invalid PID {pid} and LocalID {local_id} in game {self.gid}")
                return None

        for p in self.players:
            if p.local_id == local_id:
                return p

        self.notify.warning(f"[get_player] No player with local_id {local_id} in game {self.gid}")
        return None

    """
    # PLAYER RELATED
    """

    def generate_local_id(self):
        """
        @return: an available local_id
        @rtype: int
        """
        self.notify.debug("[generate_local_id] Generating a LocalID!")
        local_id = len(self.players)
        while local_id in self.get_local_id_pool():
            local_id += 1
            if local_id >= 255:
                # i'd hope it'd never get it but just in case i guess
                self.notify.error(f"[generate_local_id] local_id {local_id} is too high! Maximum 255!")
                break
        self.notify.debug(f"[generate_local_id] Generated LocalID {local_id}")
        return local_id

    def add_player(self, pid):
        """
        Adds a player using the player's ID
        @param pid: The Player ID you want to add
        @type pid: int
        @return: if successful
        @rtype: bool
        """
        self.notify.debug(f"[add_player] Adding player {pid} to game {self.gid}")

        p = Player(self.generate_local_id(), pid=pid)
        self.players.append(p)

        self.notify.debug(f"[add_player] List of players now: {self.players}")

        if self.message_all_players(dg_add_player(p.local_id), exclude=[p.local_id]):
            # send all players to the new player
            for existing in self.players:
                if not self.message_player(dg_add_player(existing.local_id, existing.name),
                                           p.local_id):
                    return False
        else:
            return False
        return True

    def add_ai(self):
        # self.notify.debug(f"[add_ai] Adding AI to game {self.gid}")
        p = AI(self.generate_local_id())
        self.players.append(p)
        return self.message_all_players(dg_add_player(p.local_id, p.name))

    def remove_player(self, local_id=None, pid=None):
        """
        Removes player using their Local ID
        @param local_id: the palyer's local ID
        @type local_id: int
        @param pid: the player's PID
        @type pid: int
        @return: if successful
        @rtype: bool
        """
        self.notify.debug(f"[remove_player] Removing LocalID {local_id} / PID {pid} from game {self.gid}")

        if local_id is None:
            local_id = self.get_local_id_from_pid(pid)
            if local_id is None:
                self.notify.warning(f"[remove_player] Called with invalid LocalID {local_id} and PID {pid} on"
                                    f" game {self.gid}")

        # needs to be done before they're removed because we use their data
        if self.started:
            if not self.message_all_players(dg_has_died(local_id), exclude=[local_id]):
                self.notify.warning(f"[remove_player] Failed to message all players that {local_id} has"
                                    f" died!")
                return False
        else:
            if not self.message_all_players(dg_remove_player(local_id), exclude=[local_id]):
                self.notify.warning(f"[remove_player] Failed to message all players that {local_id} has "
                                    f"left the lobby!")
                return False

        # now delete their data
        self.players.remove(self.get_player(local_id=local_id))

        # check if game needs to be deleted
        if not self.any_real_players():
            self.delete_this_game()
            return True

        # re-verify vote to start
        if self.started:
            self.verify_vote_to_start()

        return True

    def set_name(self, local_id=None, pid=None, name="???"):
        """
        Set the player's name
        @return: if successful
        @rtype: bool
        """
        if local_id is None:
            local_id = self.get_local_id_from_pid(pid)
            if local_id is None:
                self.notify.warning(f"[set_name] No PID {pid} or local_id {local_id} given!")

        # TODO validate name
        self.notify.debug(f"[set_name] Changing name of local player {local_id} to {name} in game {self.gid}")

        player = self.get_player(local_id=local_id)
        if player:
            player.name = name
            return self.message_all_players(dg_update_player_name(local_id, name))

        self.notify.warning(f"[set_name] Attempted to change local player {local_id} to {name} in game "
                            f"{self.gid}, but local player {local_id} does not exist!")

        return False

    def vote_to_start(self, pid):
        """
        Set the player's Vote to Start status
        @param pid: Player ID
        @type pid: int
        @return: If successful
        @rtype: bool
        """
        if not self.started:
            p = self.get_player(pid=pid)
            if p:
                p.voted_to_start = True
                self.verify_vote_to_start()
                return True
            else:
                self.notify.warning(f"[vote_to_start] No player with PID {pid} in game {self.gid}!")
                self.notify.warning(f"[vote_to_start] List of players: {self.players}")
        else:
            self.notify.warning(f"[vote_to_start] Vote to start from {pid} after game {self.gid}"
                                f" already started!")
        return False

    def set_player_room(self, pid, room):
        """
        Set the desired room for a player
        @param pid: the player's PID
        @type pid: int
        @param room: the room that they desire
        @type room: int
        @return: if successful
        @rtype: bool
        """
        if self.day:
            player = self.get_player(pid=pid)
            if player:
                player.room = room
                self.notify.debug(f"[set_player_room] Set player {pid}'s room to {room} in game {self.gid}")
                return True
            else:
                self.notify.warning(f"[set_player_room] Attempted to set non-existent player {pid}'s room"
                                    f" to {room} in game {self.gid}!")
        else:
            self.notify.warning("{} tried to set room during night".format(pid))
        return False

    def set_kill_choice(self, pid, choice):
        """
        Set if the killer wants to kill or not
        @param pid: the player's PID
        @type pid: int
        @param choice: Do they want to kill?
        @type choice: bool
        @return: if successful
        @rtype: bool
        """
        player = self.get_player(pid=pid)
        if player is not None:
            if self.killer == player.local_id:
                player.wants_to_kill = choice
                return True
            else:
                self.notify.warning(f"[set_kill_choice] Player {pid} tried to set kill choice,"
                                    f" but they're not the killer {self.killer} in game {self.game}")
        else:
            self.notify.warning(f"[set_kill_choice] Could not find a player with the PID {pid} in game"
                                f" {self.gid}!")
        return False

    """
    # DATA RETRIEVAL
    """

    def get_player_count(self):
        """
        @return: The amount of players in the game
        @rtype: int
        """
        return len(self.players)

    def get_vote_count(self):
        """
        Finds out how many players have voted to start the game
        @return: Number of players who have Voted to Start
        @rtype: int
        """
        count = 0
        for p in self.players:
            if p.voted_to_start:
                count += 1
        return count

    def get_players_in_room(self, room, include_killer):
        """
        Gets a list of players' local IDs in a room
        @param room: the room to search
        @type room: int
        @param include_killer: should we include the killer in this search?
        @type include_killer: bool
        @return: the list of players' local IDs in a room
        @rtype: list
        """
        in_room = []
        for p in self.players:
            if include_killer:
                if p.room == room:
                    in_room.append(p.local_id)
            else:
                if p.room == room and p.local_id != self.killer:
                    in_room.append(p.local_id)
        return in_room

    def get_local_id_pool(self):
        """
        get every currently taken local_id
        @return: list of local_ids
        @rtype: list
        """
        self.notify.debug("[get_local_id_pool] Getting the LocalID pool...")
        local_ids = []
        for p in self.players:
            local_ids.append(p.local_id)
        self.notify.debug(f"[get_local_id_pool] Generated LocalID pool: {local_ids}")
        return local_ids

    def any_real_players(self):
        """
        Checks if there's any real players left in the game
        @return: if there's any real players left in the game
        @rtype: bool
        """
        for p in self.players:
            if not p.ai:
                return True
        return False

    def check_if_available(self):
        """
        Checks requirements for a game to be available to join
        @return: if available
        @rtype: bool
        """
        return self.open and not self.started

    def verify_vote_to_start(self):
        """
        Called to verify if the game should start. Should be called when players leave lobbies or cast
        their vote.
        @return: if the vote passes
        @rtype: bool
        """
        vote_count = self.get_vote_count()
        player_count = self.get_player_count()

        if vote_count / player_count >= 0.75:
            self.notify.debug("[verify_vote_to_start] Vote start passed! Start game!")
            self.start_game()
            return True
        else:
            self.message_all_players(dg_update_vote_count(vote_count))
            return False

    """
    # GAME FUNCTIONS
    """

    def start_game(self):
        """
        Called upon the game starting for the first time
        """
        self.notify.debug(f"[start_game] Starting game: {self.gid}")

        # set variables
        self.started = True
        self.day_count = 1

        # create AI
        while self.get_player_count() < MAX_PLAYERS:
            self.add_ai()

        # fix people who haven't updated their name
        for p in self.players:
            if p.name == "???":
                self.set_name(p.local_id, p.random_name())

        # assign killer
        # TODO
        #   make it random and not just the first player - but i need to debug
        self.killer = self.players[0].local_id

        # tell players
        self.message_all_players(dg_start_game(self))

        # tell killer
        self.message_killer(dg_you_are_killer())

        # create task to change time of day
        taskMgr.doMethodLater(TIME, self.change_time, "DayNight Cycle {}".format(self.gid))

    def change_time(self, taskdata):
        self.day = not self.day
        if self.day:
            self.change_to_day()
        else:
            self.change_to_night()

        return Task.again

    def change_to_day(self):
        self.notify.debug(f"[change_to_day] Changing time to day in game {self.gid}")

        self.day_count += 1

        # check if changing day count put us over the limit
        if self.day_count > MAX_DAYS:
            self.notify.debug(f"[change_to_day] Maximum day_count reached: {self.day_count}/{MAX_DAYS}")
            self.delete_this_game()
            return Task.done

        # check if killer wants to kill
        killer = self.get_player(local_id=self.killer)
        if killer.wants_to_kill:
            # KILL
            self.red_room = killer.room
            possible_victims = self.get_players_in_room(self.red_room, False)
            if len(possible_victims) > 0:
                # select random
                victim = random.choice(possible_victims)

                self.notify.debug(f"[change_to_day] Killing {victim} in {self.gid}")

                if self.get_player(local_id=victim).ai:
                    self.remove_player(local_id=victim)
                else:
                    self.msgr.remove_player_from_game(self.get_pid_from_local_id(victim), KILLED)

                    # check if need to end game due to lack of players
                    if not self.any_real_players():
                        self.notify.debug(f"[change_to_day] No non-ai players in game {self.gid}")
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
            p.room = None

        # reset killer's choice
        killer.wants_to_kill = False

        self.message_all_players(dg_goto_day(self))

    def change_to_night(self):
        for p in self.players:
            # run ai
            if p.ai:
                p.night_run()
            else:
                # make sure every one's picked a room, if they haven't give them a random one
                if not p.room:
                    p.random_room()
        # now that everyone is in their room, tell everyone how many are with them
        for p in self.players:
            if not p.ai:
                self.message_player(dg_how_many_in_room(len(self.get_players_in_room(p.room, True)) - 1),
                                    p.local_id)

        self.message_all_players(dg_goto_night(self))

    def delete_this_game(self):
        self.notify.debug(f"[delete_this_game] Deleting game {self.gid}")

        # end tasks
        taskMgr.remove("DayNight Cycle {}".format(self.gid))

        # tell clients
        self.message_all_players(dg_kick_from_game(GAME_DELETED))

        # tell msgr to delete this game
        self.msgr.delete_game(self.gid)
