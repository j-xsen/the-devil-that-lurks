from direct.directnotify.DirectNotifyGlobal import directNotify
from objects.player import Player


class AI(Player):
    notify = directNotify.newCategory("ai")

    def __init__(self, _local_id):
        Player.__init__(self, _local_id, _ai=True)

    def get_connection(self):
        self.notify.warning("Someone request AI's connection...")
        return False
