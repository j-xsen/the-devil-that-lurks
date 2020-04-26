# UberDOG
from direct.distributed.DistributedObjectGlobal import DistributedObjectGlobal
from direct.distributed.DistributedObjectGlobalAI import DistributedObjectGlobalAI
from direct.distributed.DistributedObjectGlobalUD import DistributedObjectGlobalUD

# DOG
from direct.distributed.DistributedObject import DistributedObject
from direct.distributed.DistributedObjectAI import DistributedObjectAI
from direct.distributed.DistributedObjectUD import DistributedObjectUD
from direct.distributed.DistributedObjectOV import DistributedObjectOV

# DOs that are graph nodes
from direct.distributed.DistributedNode import DistributedNode
from direct.distributed.DistributedNodeAI import DistributedNodeAI

# Notify
from direct.directnotify.DirectNotify import DirectNotify
notify_ud = DirectNotify().newCategory("ud")
notify_server = DirectNotify().newCategory("server")

# Assembling messages
from direct.distributed.PyDatagram import PyDatagram
from direct.distributed import MsgTypes
from direct.distributed.AstronInternalRepository import AstronInternalRepository

# AI tasks
from direct.task import Task

# # # LoginManager
# # Auths client
# # MAkes maproot & creates empty player
class DistributedLoginManager(DistributedObjectGlobal):
    def login(self, name):
        self.sendUpdate("login", [name])

class DistributedLoginManagerAI(DistributedObjectGlobalAI):
    def set_maproot(self, maproot_doId):
        self.sendUpdate("set_maproot", [maproot_doId])

class DistributedLoginManagerUD(DistributedObjectGlobalUD):
    def set_maproot(self, maproot_doId):
        # Tells the DistributedLoginManagerUD what maproot to notify on login
        self.maproot = DistributedMaprootUD(self.air)
        self.maproot.generateWithRequiredAndId(maproot_doId, 0, 1)

    def login(self, name):
        clientId = self.air.get_msg_sender()

        # verify
        if name:
            # Set CLIENT_STATE_ESTABLISHED
            self.air.setClientState(clientId, 2)

            # now that auth, create player
            self.maproot.sendUpdate("create_character_ov", [clientId])

            # notify
            notify_ud.info("Login successful for {}".format(name))
        else:
            # disconnect for bad auth
            self.air.eject(clientId, 122, "Bad Credentials")

            # notify
            self.notify.info("Ejecting client for bad credentials: {}".format(name))

# # # MapRoot
# # Games in zone 1
# # Unassigned players zone 0

class DistributedMaproot(DistributedObject):
    pass

class DistributedMaprootOV(DistributedObjectOV):
    pass

class DistributedMaprootAI(DistributedObjectAI):
    def generate(self):
        pass

    def create_character_ov(self, clientId):
        # create the blank character
        character = DistributedPlayerAI(self.air)
        character.generateWithRequiredAndId(self.air.allocateChannel(), self.getDoId(), 0)
        self.air.setOwner(character.getDoId(), clientId)
        self.air.clientAddSessionObject(clientId, character.getDoId())

class DistributedMaprootUD(DistributedObjectUD):
    def generate(self):
        pass

    def create_character_ov(self, clientId):
        self.sendUpdate("create_character_ov", [clientId])

# # # Distributed Character

class DistributedPlayer(DistributedNode):
    def generateInit(self):
        print("TEST11")
        # base.messenger.send("new_player", [self])
        pass

class DistributedPlayerOV(DistributedObjectOV):
    def generateInit(self):
        # make known to client
        print("TEST")
        base.messenger.send("heres_your_player", [self])

class DistributedPlayerAI(DistributedNodeAI):
    def generate(self, repository = None):
        # what to do server-side
        print("WHAT")
        pass

    def delete(self):
        # remove
        pass