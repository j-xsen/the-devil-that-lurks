class ConnectionHolder:
    def __init__(self, connection, pid):
        self.connection = connection
        self.gid = None
        self.heartbeat = True
        self.pid = pid
        pass