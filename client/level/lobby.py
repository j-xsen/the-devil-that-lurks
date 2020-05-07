from level.level import Level

from direct.gui.OnscreenText import OnscreenText
from direct.gui.DirectGui import DirectButton

from communicator import dg_vote_to_start


class LobbyLevel(Level):
    def __init__(self, father):
        Level.__init__(self, "Lobby", "img/egg/mainmenu.egg", father)
        self.votes = 0
        self.players_count = 0

    def create(self):
        self.text = []
        self.buttons = []

        txt_players = OnscreenText(text="Players", pos=(0, 0.5), scale=0.35, fg=(1, 1, 1, 1))
        txt_current = OnscreenText(text="0/9", pos=(0, 0), scale=0.2, fg=(1, 1, 1, 1))
        txt_votes = OnscreenText(text="0/0", pos=(0, -0.75), scale=0.2, fg=(1, 1, 1, 1))

        btn_vote = DirectButton(text="Vote to start", scale=0.1, pos=(0, 0, -0.5), command=self.vote_to_start)

        self.text.append(txt_current)
        self.text.append(txt_players)
        self.text.append(txt_votes)
        self.buttons.append(btn_vote)

    # for transitions between screens on this level
    # just destroy self.images and self.buttons
    def soft_destroy(self):
        for b in self.buttons:
            self.destroy_button(b)
        for t in self.text:
            self.destroy_image(t)

    def vote_to_start(self):
        self.father.write(dg_vote_to_start(self.father.pid))

    def update_player_count(self, count):
        self.players_count = count
        self.text[0].text = "{}/9".format(count)
        self.text[2].text = "{}/{}".format(self.votes, count)

    def update_vote_count(self, votes):
        self.votes = votes
        self.text[2].text = "{}/{}".format(votes, self.players_count)
