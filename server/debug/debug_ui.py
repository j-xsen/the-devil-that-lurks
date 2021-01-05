from direct.showbase.DirectObject import DirectObject
from debug.objects.games_list import GamesList
from debug.objects.single_game import SingleGame
from debug.objects.players_list import PlayersList
from debug.objects.single_player import SinglePlayer
from objects.notifier import Notifier
from direct.task.TaskManagerGlobal import taskMgr


class DebugUI(DirectObject, Notifier):

    def __init__(self, messager):
        DirectObject.__init__(self)
        Notifier.__init__(self, "ui")

        self.messager = messager
        self.games_list = GamesList(self)
        self.players_all = PlayersList(self)

        self.single_game = SingleGame(messager)
        self.single_player = SinglePlayer(self)

        # True for game, False for player
        self.single_game_or_player = True

        self.notify.info("[__init__] Created DebugUI")

    def change_gid(self, new_gid):
        if self.single_game_or_player:
            self.single_game.change_gid(new_gid)
        else:
            self.single_player.change_pid(None)
            self.single_game_or_player = True
            self.single_game.change_gid(new_gid)

    def change_pid(self, new_pid):
        if not self.single_game_or_player:
            self.single_player.change_pid(new_pid)
        else:
            self.single_game.change_gid(None)
            self.single_game_or_player = False
            self.single_player.change_pid(new_pid)

    def switch_list(self, new_list):
        """
        @param new_list: The new list to display. 1 for GamesList, 2 for PlayersAll
        @type new_list: int
        """
        if new_list == 1:
            self.notify.debug("[switch_list] Changing list to GamesList")
            self.players_all.change_active(False)
            self.games_list.change_active(True)
        else:
            self.notify.debug("[switch_list] Changing list to PlayersAll")
            self.games_list.change_active(False)
            self.players_all.change_active(True)
