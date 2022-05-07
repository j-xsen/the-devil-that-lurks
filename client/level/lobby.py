from level.level import Level

from direct.gui.OnscreenText import OnscreenText
from direct.gui.DirectGui import DirectButton
from objects.entry import Entry
from objects.checkbox import Checkbox

from communications.datagrams import dg_vote_to_start, dg_leave_lobby, dg_update_name


class LobbyLevel(Level):

    multifiles = "art.mf"

    def __init__(self, father):
        Level.__init__(self, "Lobby", self.multifiles, father)
        self.votes = 0
        self.players_count = 0

    def create(self):
        txt_players = OnscreenText(text="0/9", pos=(0, 0), scale=0.2, fg=(1, 1, 1, 1))
        txt_names = OnscreenText(text="", pos=(-.925, -0.15), scale=0.1, fg=(1, 1, 1, 1))
        txt_votes = OnscreenText(text="0/0", pos=(0, -0.75), scale=0.2, fg=(1, 1, 1, 1))
        txt_gid = OnscreenText(text="22222", pos=(0, 0.5), scale=0.1, fg=(1, 1, 1, 1))

        btn_vote = DirectButton(text="Vote to start", scale=0.1, pos=(0, 0, -0.5), command=self.vote_to_start)
        btn_leave = DirectButton(text="Leave Lobby", scale=0.1, pos=(0.75, 0, 0), command=self.leave)

        entry_name = Entry("Enter a name", (-1, 0, 0), self.update_name)

        self.text["txt_names"] = txt_names
        self.text["txt_players"] = txt_players
        self.text["txt_votes"] = txt_votes
        self.text["txt_gid"] = txt_gid
        self.gui["btn_vote"] = btn_vote
        self.gui["btn_leave"] = btn_leave
        self.gui["entry_name"] = entry_name

    def vote_to_start(self):
        self.messager.write(dg_vote_to_start(self.messager.pid))

    def leave(self):
        self.messager.write(dg_leave_lobby(self.messager.pid))

    def set_gid(self, gid):
        self.text["txt_gid"].text = f"Game ID: {gid}"

    def update_player(self):
        """
        Updates all the player-dependent info (List of names & Count)
        """
        self.update_player_list()
        self.update_player_count()

    def update_player_list(self):
        """
        Updates list of player names
        """
        # get list from father
        names = ""
        for local_id in self.level_holder.players:
            names += "{}\n".format(self.level_holder.players[local_id].name)

        # display
        self.text["txt_names"].text = names

    def update_player_count(self):
        """
        Updates the player count information
        """
        self.players_count = len(self.level_holder.players)
        self.text["txt_players"].text = "{}/9".format(self.players_count)
        self.text["txt_votes"].text = "{}/{}".format(self.votes, self.players_count)

    def update_vote_count(self, votes):
        """
        Updates the vote count information and displays it
        @param votes: the amount of votes FOR starting
        @type votes: int
        """
        self.votes = votes
        self.text["txt_votes"].text = "{}/{}".format(votes, self.players_count)

    def update_name(self, name):
        self.messager.write(dg_update_name(self.messager.pid, name))
