from communications.codes import *
from communications.communicator import dg_send_heartbeat
from direct.distributed.PyDatagramIterator import PyDatagramIterator
from direct.directnotify.DirectNotifyGlobal import directNotify
from objects.alert import Alert
from direct.task.TaskManagerGlobal import taskMgr, Task
from panda3d.core import NetDatagram


# this class takes and decodes messages
class Messager:

    # notify
    notify = directNotify.newCategory("lp")

    def __init__(self, father):
        self.father = father

    def received_code(self, taskdata):
        """
        Called when the client is given a datagram.
        This gets the information from said datagram and calls whatever function necessary
        @param self
        @param taskdata
        """
        if self.father.cReader.dataAvailable():
            dg = NetDatagram()
            if self.father.cReader.getData(dg):
                iterator = PyDatagramIterator(dg)

                try:
                    msg_id = iterator.getUint8()
                except AssertionError:
                    self.notify.warning("Invalid msg_id")
                    return Task.cont

                if msg_id in self.mapping:
                    self.mapping[msg_id](self, iterator)
                else:
                    self.notify.warning("Unknown msg_id: {}".format(msg_id))
        return Task.cont

    def heartbeat(self, taskdata):
        """
        Called on a regular interval to tell the server we're still here
        """
        self.father.write(dg_send_heartbeat(self.father.pid))
        return Task.again

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
        if not self.father.pid:
            try:
                pid = iterator.getUint16()
            except AssertionError:
                self.notify.warning("Invalid DELIVER_PID")
                return False

            self.notify.debug("Received PID: {}".format(pid))
            self.father.pid = pid
        else:
            self.notify.warning("Received PID after already receiving one")

        return True

    def game_received(self, iterator):
        """
        Called when server gives client a game
            uint8 - player_count: the amount of players in the lobby
            uint8 - vote_count: the amount of votes to start the game
        @return If successful
        @rtype bool
        """
        # check if valid
        try:
            player_count = iterator.getUint8()
            vote_count = iterator.getUint8()
        except AssertionError:
            self.notify.warning("Invalid DELIVER_GAME")
            return False

        # if father is on main menu, send them to lobby
        if self.father.active_level.name == "Main Menu":
            self.father.set_active_level("Lobby")
            self.father.active_level.update_player_count(player_count)
            self.father.active_level.update_vote_count(vote_count)
        else:
            self.notify.warning("Received a game while in a game")

        return True

    def kicked_from_game(self, iterator):
        """
        Called when player is kicked from a game
            uint8 - Reason
        @return: if successful
        @rtype: bool
        """
        self.father.set_active_level("Main Menu")

        try:
            reason = iterator.getUint8()
        except AssertionError:
            self.notify.warning("Invalid KICKED_FROM_GAME")
            return False

        # need we tell them that they hit leave game?
        if reason != LEFT_GAME:
            Alert(reason)

    def killed_connection(self, iterator):
        """
        Called when the server kills the connection
        @return: if successful
        @rtype: bool
        """
        # TODO show error on mainmenu
        self.notify.debug("Connection has been killed")
        return True

    def update_player_count(self, iterator):
        """
        Called when server sends an updated player count
        @return: if successful
        @rtype: bool
        """
        if self.father.active_level.name == "Lobby":
            try:
                player_count = iterator.getUint8()
            except AssertionError:
                self.notify.warning("Invalid UPDATE_PLAYER_COUNT")
                return False

            self.father.active_level.update_player_count(player_count)
        else:
            self.notify.warning("update_player_count called when not in lobby")
            return False

        return True

    def update_vote_count(self, iterator):
        """
        Called when server sends an updated vote count
        @return: if successful
        @rtype: bool
        """
        if self.father.active_level.name == "Lobby":
            try:
                vote_count = iterator.getUint8()
            except AssertionError:
                self.notify.warning("Invalid UPDATE_VOTE_COUNT")
                return False

            self.father.active_level.update_vote_count(vote_count)
        else:
            self.notify.warning("update_vote_Count called when not in lobby")
            return False

        return True

    def start_game(self, iterator):
        """
        Called when the server tells client that the game has started
        @return: if successful
        @rtype: bool
        """
        if self.father.active_level.name == "Lobby":
            players = {}
            i = 0
            while i < MAX_PLAYERS:
                try:
                    name = iterator.getString()
                    local_id = iterator.getUint8()
                    players[local_id] = {"name": name}
                except AssertionError:
                    self.notify.warning("Invalid START_GAME")
                    return False
                i += 1

            self.father.players = players
            self.father.day = 0
            self.father.set_active_level("Day")
        else:
            self.notify.warning("start_game while not in lobby")
            return False

        return True

    def you_are_killer(self, iterator):
        """
        Called when server tells client that they are the killer
        @return: if successful
        @rtype: bool
        """
        self.father.killer = True
        return True

    def has_died(self, iterator):
        """
        Called when server tells client that someone has died
        @return: if successful
        @rtype: bool
        """
        try:
            the_dead = iterator.getUint8()
        except AssertionError:
            self.notify.warning("Invalid HAS_DIED")
            return False

        self.father.dead.append(the_dead)

        return True

    def goto_day(self, iterator):
        """
        Called when the server says it is day
        @return: if successful
        @rtype: bool
        """
        if self.father.active_level.name != "Main Menu":
            try:
                day_count = iterator.getUint8()
            except AssertionError:
                self.notify.warning("Invalid GOTO_DAY")
                return False

            self.father.goto_day(day_count)
        else:
            self.notify.warning("goto_day while not in game")
            return False

        return True

    def goto_night(self, iterator):
        """
        Called when the server says it is night
        @return: if successful
        @rtype: bool
        """
        if self.father.active_level.name != "Main Menu":
            self.father.goto_night()
        else:
            self.notify.warning("goto_night while not in game")
            return False
        return True

    def kill_failed_empty_room(self, iterator):
        """
        Called when the server says kill failed due to empty room
        @return: if successful
        @rtype: bool
        """
        # TODO do something with this
        self.notify.debug("Failed to kill! Empty room!")

    def number_in_room(self, iterator):
        """
        Called when the server tells client how many players in their room
        @return: if successful
        @rtype: bool
        """
        try:
            num = iterator.getUint8()
            self.father.level_night.set_players_here(num)
        except AssertionError:
            self.notify.warning("Invalid NUM_IN_ROOM")
            return False

        return True

    # define what functions go with what codes here
    mapping = {
        DELIVER_PID: pid_received,
        DELIVER_GAME: game_received,
        KICKED_FROM_GAME: kicked_from_game,
        KILLED_CONNECTION: killed_connection,
        UPDATE_PLAYER_COUNT: update_player_count,
        UPDATE_VOTE_COUNT: update_vote_count,
        START_GAME: start_game,
        YOU_ARE_KILLER: you_are_killer,
        HAS_DIED: has_died,
        GOTO_DAY: goto_day,
        GOTO_NIGHT: goto_night,
        KILL_FAILED_EMPTY_ROOM: kill_failed_empty_room,
        NUM_IN_ROOM: number_in_room
    }