from level.level import Level

from direct.gui.OnscreenText import OnscreenText
from direct.gui.DirectGui import DirectButton
from objects.entry import Entry

from communications.datagrams import dg_vote_to_start, dg_leave_lobby, dg_update_name


class LobbyLevel(Level):

    multifiles = []

    def __init__(self, father):
        Level.__init__(self, "Lobby", self.multifiles, father)
        self.votes = 0
        self.players_count = 0

    def create(self):
        self.text = []
        self.buttons = []

        txt_players = OnscreenText(text="Players", pos=(0, 0.5), scale=0.35, fg=(1, 1, 1, 1))
        txt_names = OnscreenText(text="", pos=(-.925, -0.15), scale=0.1, fg=(1, 1, 1, 1))
        txt_current = OnscreenText(text="0/9", pos=(0, 0), scale=0.2, fg=(1, 1, 1, 1))
        txt_votes = OnscreenText(text="0/0", pos=(0, -0.75), scale=0.2, fg=(1, 1, 1, 1))

        btn_vote = DirectButton(text="Vote to start", scale=0.1, pos=(0, 0, -0.5), command=self.vote_to_start)
        btn_leave = DirectButton(text="Leave Lobby", scale=0.1, pos=(0.75, 0, 0), command=self.leave)

        entry_name = Entry("Enter a name", (-1, 0, 0), self.update_name)

        self.text.append(txt_current)
        self.text.append(txt_names)
        self.text.append(txt_players)
        self.text.append(txt_votes)
        self.gui.append(btn_vote)
        self.gui.append(btn_leave)
        self.gui.append(entry_name)

    def vote_to_start(self):
        self.father.write(dg_vote_to_start(self.father.pid))

    def leave(self):
        self.father.write(dg_leave_lobby(self.father.pid))

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
        for p in self.father.players:
            names += "{}\n".format(self.father.players[p]["name"])

        # display
        self.text[1].text = names

    def update_player_count(self):
        """
        Updates the player count information
        """
        self.players_count = len(self.father.players)
        self.text[0].text = "{}/9".format(self.players_count)
        self.text[3].text = "{}/{}".format(self.votes, self.players_count)

    def update_vote_count(self, votes):
        """
        Uppdates the vote count information
        @param votes: the amount of votes FOR starting
        @type votes: int
        """
        self.votes = votes
        self.text[3].text = "{}/{}".format(votes, self.players_count)

    def update_name(self, name):
        self.father.write(dg_update_name(self.father.pid, name))
