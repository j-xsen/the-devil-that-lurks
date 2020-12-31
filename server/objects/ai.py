from direct.directnotify.DirectNotifyGlobal import directNotify
from objects.player import Player
from objects.notifier import Notifier


class AI(Player, Notifier):
    def __init__(self, local_id):
        Player.__init__(self, local_id, ai=True)
        Notifier.__init__(self, "ai")
        self.random_name()

    # this is ran going into night
    def night_run(self):
        """
        What to do upon going to night
        :return:
        :rtype:
        """
        # select room
        self.random_room()
