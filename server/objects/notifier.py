from direct.directnotify.DirectNotifyGlobal import directNotify


class Notifier:
    def __init__(self, name):
        """
        @param name: The name of the notifier. Be sure to add it to your config/Config.prc!
        @type name: str
        """
        self.notify = directNotify.newCategory(name)
