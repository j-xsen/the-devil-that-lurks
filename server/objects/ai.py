from direct.directnotify.DirectNotifyGlobal import directNotify
from objects.player import Player


class AI(Player):
    notify = directNotify.newCategory("ai")

    def __init__(self, local_id):
        Player.__init__(self, local_id, ai=True)
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
