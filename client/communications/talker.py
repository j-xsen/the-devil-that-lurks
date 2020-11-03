# inherit from this class if you need to talk

class Talker:
    def __init__(self):
        return

    def write(self, dg):
        """
        Sends message to server
        @param dg: datagram you want to send
        @type dg: direct.distributed.PyDatagram.PyDatagram
        @return: if message sends
        @rtype: bool
        """
        if self.my_connection:
            return self.cWriter.send(dg, self.my_connection)
        else:
            Alert(-2)
            self.notify.warning("No connection to send message to!")
        return False
