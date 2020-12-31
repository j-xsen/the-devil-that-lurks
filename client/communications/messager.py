from communications.codes import *
from communications.datagrams import dg_send_heartbeat
from level.codes import *
from direct.distributed.PyDatagramIterator import PyDatagramIterator
from direct.directnotify.DirectNotifyGlobal import directNotify
from objects.alert import Alert
from direct.task.TaskManagerGlobal import Task
from panda3d.core import NetDatagram


"""

This class receives and decodes messages

"""


class Messager:

    # notify
    notify = directNotify.newCategory("messager")

    def __init__(self, _cWriter, _cManager, _cReader, level_holder):
        self.notify.setDebug(True)
        self.cWriter = _cWriter
        self.cManager = _cManager
        self.cReader = _cReader
        self.my_connection = None
        self.pid = None
        self.level_holder = level_holder
        self.notify.debug("[__init__] Created messager")

    def check_for_message(self, taskdata):
        """
        Called repeatedly to check if any new messages from server
        This gets the information from said datagram and calls whatever function necessary
        @param self
        @param taskdata
        """
        if self.cReader.dataAvailable():
            dg = NetDatagram()
            if self.cReader.getData(dg):
                iterator = PyDatagramIterator(dg)

                try:
                    msg_id = iterator.getUint8()
                except AssertionError:
                    self.notify.warning("[check_for_message] Invalid msg_id!")
                    return Task.cont

                if msg_id in self.mapping:
                    self.mapping[msg_id](self, iterator)
                else:
                    self.notify.warning(f"[check_for_message] Unknown msg_id: {msg_id}")
        return Task.cont

    def heartbeat(self, taskdata):
        """
        Called on a regular interval to tell the server we're still here
        """
        self.write(dg_send_heartbeat(self.pid))
        return Task.again

    def write(self, dg):
        if self.my_connection:
            return self.cWriter.send(dg, self.my_connection)
        else:
            Alert(-2)
            self.notify.warning("[write] No connection to send message to!")
        return False

    #
    # MESSAGE CODES
    #

    def pid_received(self, iterator):
        """
        Called when server gives client a player ID
            uint16 - pid: the client's player ID
        @return If successful
        @rtype bool
        """
        if not self.pid:
            try:
                pid = iterator.getUint16()
            except AssertionError:
                self.notify.warning("[pid_received] Invalid DELIVER_PID")
                return False

            self.notify.debug(f"[pid_received] Received PID: {pid}")
            self.pid = pid
            return True
        else:
            self.notify.warning("[pid_received] Received PID after already receiving one")
        return False

    def game_received(self, iterator):
        """
        Called when server gives client a game
            uint16 - gid: The GID
            uint8 - vote_count: the amount of votes to start the game
        @return: If successful
        @rtype: bool
        """
        # check if valid
        try:
            gid = iterator.getUint16()
            vote_count = iterator.getUint8()
        except AssertionError:
            self.notify.warning("[game_received] Invalid DELIVER_GAME!")
            return False

        self.notify.debug(f"[game_received] Received game {gid} with a vote count of {vote_count}")

        # if father is on main menu, send them to lobby
        if self.level_holder.active_level == MAINMENU:
            self.level_holder.set_active_level(LOBBY)
            self.level_holder.levels[LOBBY].update_vote_count(vote_count)
            self.level_holder.levels[LOBBY].set_gid(gid)
            return True
        else:
            self.notify.warning("[game_received] Received a game while in a game!")
        return False

    def kicked_from_game(self, iterator):
        """
        Called when player is kicked from a game
            uint8 - Reason
        @return: if successful
        @rtype: bool
        """
        self.level_holder.set_active_level(MAINMENU)

        try:
            reason = iterator.getUint8()
        except AssertionError:
            self.notify.warning("[kicked_from_game] Invalid KICKED_FROM_GAME!")
            return False

        self.notify.debug(f"[kicked_from_game] Kicked from game for reason {reason}.")

        # need we tell them that they hit leave game?
        if reason != LEFT_GAME:
            Alert(reason)
        return True

    def killed_connection(self, iterator):
        """
        Called when the server kills the connection
        @return: if successful
        @rtype: bool
        """
        # TODO show error on mainmenu
        self.notify.warning("[killed_connection] Connection to server has been killed.")
        self.level_holder.set_active_level(MAINMENU)
        Alert(SERVER_KILLED_CONNECTION)
        return True

    def add_player(self, iterator):
        """
        Called when server sends a player
        @return: if successful
        @rtype: bool
        """
        if self.level_holder.active_level == LOBBY:
            try:
                new_player_id = iterator.getUint8()
                name = iterator.getString()
            except AssertionError:
                self.notify.warning("[add_player] Invalid add_player")
                return False

            self.notify.debug(f"[add_player] Received new player: {name} ({new_player_id})")
            self.level_holder.add_player(new_player_id, name)
        else:
            self.notify.warning("[add_player] Called when not in lobby!")
            return False

        return True

    def remove_player(self, iterator):
        """
        Called when server removes a player. this should only be called by server while in lobby
        @return: if successful
        @rtype: bool
        """
        if self.level_holder.active_level == LOBBY:
            try:
                ex_player_id = iterator.getUint8()
            except AssertionError:
                self.notify.warning("[remove_player] Invalid remove_player!")
                return False
            self.notify.debug(f"[remove_player] Player {ex_player_id} is being removed.")
            self.level_holder.remove_player(ex_player_id)
            return True
        else:
            self.notify.warning("[remove_player] Called when not in lobby!")
            # TODO check if in game, and just kill the player if true
        return False

    def update_vote_count(self, iterator):
        """
        Called when server sends an updated vote count
        @return: if successful
        @rtype: bool
        """
        if self.level_holder.active_level == LOBBY:
            try:
                vote_count = iterator.getUint8()
            except AssertionError:
                self.notify.warning("[update_vote_count] Invalid UPDATE_VOTE_COUNT")
                return False
            self.notify.debug(f"[update_vote_count] Received updated vote count: {vote_count}")
            self.level_holder.levels[LOBBY].update_vote_count(vote_count)
            return True
        else:
            self.notify.warning("[update_vote_count] Called when not in lobby!")
        return False

    def update_name(self, iterator):
        """
        Called when server tells us a player has changed their name
        @return: if successful
        @rtype: bool
        """
        try:
            local_id = iterator.getUint8()
            new_name = iterator.getString()
        except AssertionError:
            self.notify.warning("[update_name] Invalid update_name")
            return False

        self.notify.debug(f"[update_name] Received new name {new_name} for player {local_id}")
        return self.level_holder.update_name(local_id, new_name)

    def start_game(self, iterator):
        """
        Called when the server tells client that the game has started
        @return: if successful
        @rtype: bool
        """
        self.notify.debug("[start_game] Starting game!")
        if self.level_holder.active_level == LOBBY:
            self.level_holder.set_active_level(DAY)
            return True
        else:
            self.notify.warning("[start_game] Called while not in lobby")
        return False

    def you_are_killer(self, iterator):
        """
        Called when server tells client that they are the killer
        @return: if successful
        @rtype: bool
        """
        self.notify.debug("[you_are_killer] We have been told that we are the killer!")
        self.level_holder.killer = True
        return True

    def has_died(self, iterator):
        """
        Called when server tells client that someone has died
            uint8 - the local_id of the dead person
        @return: if successful
        @rtype: bool
        """
        try:
            the_dead = iterator.getUint8()
        except AssertionError:
            self.notify.warning("[has_died] Invalid HAS_DIED")
            return False

        self.notify.debug(f"[has_died] Player {the_dead} is dead.")
        self.level_holder.players[the_dead].alive = False
        return True

    def goto_day(self, iterator):
        """
        Called when the server says it is day
        @return: if successful
        @rtype: bool
        """
        if self.level_holder.active_level != MAINMENU:
            try:
                day_count = iterator.getUint8()
                red_room = iterator.getUint8()
            except AssertionError:
                self.notify.warning("[goto_day] Invalid GOTO_DAY")
                return False
            self.notify.debug("[goto_day] Server says it is day time")
            self.level_holder.day = day_count
            self.level_holder.set_active_level(DAY)
            return True
        else:
            self.notify.warning("[goto_day] Called while not in game")
        return False

    def goto_night(self, iterator):
        """
        Called when the server says it is night
        @return: if successful
        @rtype: bool
        """
        if self.level_holder.active_level != MAINMENU:
            self.notify.debug("[goto_night] Server says it is night time")
            self.level_holder.set_active_level(NIGHT)
        else:
            self.notify.warning("[goto_night] Called while not in game!")
        return False

    def kill_failed_empty_room(self, iterator):
        """
        Called when the server says kill failed due to empty room
        @return: if successful
        @rtype: bool
        """
        # TODO do something with this
        self.notify.debug("[kill_failed_empty_room] Failed to kill! Empty room!")

    def number_in_room(self, iterator):
        """
        Called when the server tells client how many players in their room
        @return: if successful
        @rtype: bool
        """
        try:
            num = iterator.getUint8()
        except AssertionError:
            self.notify.warning("[number_in_room] Invalid NUM_IN_ROOM")
            return False

        self.notify.debug(f"[number_in_room] Received number of people in our room: {num}")
        self.level_holder.levels[NIGHT].players_here = num
        return True

    # define what functions go with what codes here
    mapping = {
        DELIVER_PID: pid_received,
        DELIVER_GAME: game_received,
        KICKED_FROM_GAME: kicked_from_game,
        KILLED_CONNECTION: killed_connection,
        ADD_PLAYER: add_player,
        REMOVE_PLAYER: remove_player,
        UPDATE_VOTE_COUNT: update_vote_count,
        START_GAME: start_game,
        YOU_ARE_KILLER: you_are_killer,
        HAS_DIED: has_died,
        GOTO_DAY: goto_day,
        GOTO_NIGHT: goto_night,
        KILL_FAILED_EMPTY_ROOM: kill_failed_empty_room,
        NUM_IN_ROOM: number_in_room,
        UPDATE_NAME: update_name
    }
