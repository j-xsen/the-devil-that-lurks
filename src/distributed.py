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
notify_ai = DirectNotify().newCategory("ai")
notify_p = DirectNotify().newCategory("lp")

# Assembling messages
from direct.distributed.PyDatagram import PyDatagram
from direct.distributed import MsgTypes
from direct.distributed.AstronInternalRepository import AstronInternalRepository

# AI tasks
from direct.task import Task

# Globals
from globals import LoginManagerId

# # # LoginManager
# # Auths client
# # MAkes maproot & creates empty player
class DistributedLoginManager(DistributedObjectGlobal):
    def generateInit(self):
        notify_p.info("[DistributedLoginManager] generateInit() in {}".format(self.doId))

    def login(self, name):
        notify_p.info("[DistributedLoginManager] login({}) in {}".format(name, self.doId))
        self.sendUpdate("login", [name])

class DistributedLoginManagerAI(DistributedObjectGlobalAI):
    def generate(self):
        notify_ai.info("[DistributedLoginManagerAI] generate() in {}".format(self.doId))

    def set_maproot(self, maproot_doId):
        notify_ai.info("[DistributedLoginManagerAI] set_maproot({}) in{}".format(maproot_doId, self.doId))
        self.sendUpdate("set_maproot", [maproot_doId])

class DistributedLoginManagerUD(DistributedObjectGlobalUD):
    def generate(self):
        notify_ud.info("[DistributedLoginManagerUD] generate() in {}".format(self.doId))

    def set_maproot(self, maproot_doId):
        notify_ud.info("[DistributedLoginManagerUD] set_maproot({}) in {}".format(maproot_doId, self.doId))
        # tells DistributedLoginManagerUD what maproot to notify on login
        self.maproot = DistributedMaprootUD(self.air)
        self.maproot.generateWithRequiredAndId(maproot_doId, 0, 1)

    def login(self, name):
        notify_ud.info("[DistributedLoginManagerUD] login({}) in {}".format(name, self.doId))

        clientId = self.air.get_msg_sender()

        # verify
        if name:
            # set CLIENT_STATE_ESTABLISHED
            self.air.setClientState(clientId, 2)

            # client now auth'd, create avatar
            self.maproot.create_avatar(clientId)

            notify_ud.info("Login success for {} [{}]".format(name, clientId))
        else:
            # disccnnect for bad auth
            self.air.eject(clientId, 122, "Bad Credentials")

            notify_ud.info("Login failure for {} [{}]".format(name, clientId))

# # # MapRoot
# # Games in zone 1
# # Unassigned players zone 0

class DistributedMaproot(DistributedObject):
    pass

class DistributedMaprootAI(DistributedObjectAI):
    def generate(self):
        notify_ai.info("[DistributedMaprootAI] generate() in {}".format(self.doId))

    def set_maproot(self):
        notify_ai.info("[DistributedMaprootAI] set_maproot in {}".format(self.doId))
        login_manager = self.air.generateGlobalObject(LoginManagerId, 'DistributedLoginManager')
        login_manager.set_maproot(self.doId)

    def createAvatar(self, clientId):
        notify_ai.info("[DistributedMaprootAI] createAvatar({}) in {}".format(clientId, self.doId))

        # create the avatar
        avatar = DistributedAvatarAI(self.air)
        avatar.generateWithRequiredAndId(self.air.allocateChannel(), self.getDoId(), 0) # random doId, parentId, zoneId
        avatar.setAI(self.air.ourChannel)

        # self.air.clientAddInterest(clientId, 0, self.getDoId(), 1) # client, interest, parent, zone
        self.air.setOwner(avatar.getDoId(), clientId)
        # self.air.clientAddSessionObject(clientId, avatar.getDoId())

class DistributedMaprootUD(DistributedObjectUD):
    def generate(self):
        notify_ud.info("[DistributedMaprootUD] generate() in {}".format(self.doId))

    def create_avatar(self, clientId):
        notify_ud.info("[DistributedMaprootUD] create_avatar({}) in {}".format(clientId, self.doId))
        self.sendUpdate("createAvatar", [clientId])

# # # Distributed Avatar
class DistributedAvatar(DistributedNode):
    def generateInit(self):
        notify_p.info("[DistributedAvatar] generateInit() in {}".format(self.doId))
        base.messenger.send("distributed_avatar", [self])

class DistributedAvatarOV(DistributedObjectOV):
    def generateInit(self):
        notify_p.info("[DistributedAvatarOV] generateInit() in {}".format(self.doId))

        # make yourself known to client
        base.messenger.send("avatar", [self])

    def request_game(self):
        notify_p.info("[DistributedAvatarOV] request_game() in {}".format(self.doId))
        self.sendUpdate("request_game")

    def receive_game(self):
        notify_p.info("[DistributedAvatarOV] receive_game() in {}".format(self.doId))
        base.messenger.send("receive_game")

class DistributedAvatarAI(DistributedNodeAI):
    def generate(self, repository = None):
        notify_ai.info("[DistributedAvatarAI] generate() in {}".format(self.doId))

    def request_game(self):
        notify_ai.info("[DistributedAvatarAI] request_game() in {}".format(self.doId))

        # create the game
        game = DistributedGameAI(self.air)
        game.generateWithRequiredAndId(self.air.allocateChannel(), self.getLocation()[0], 0)  # random doId, parentId, zoneId
        game.setAI(self.air.ourChannel)

        self.air.clientAddInterest(self.doId, 0, game.getDoId(), 1)  # client, interest, parent, zone

        self.game = game
        self.sendUpdate("receive_game")


# # # DistributedGame

class DistributedGame(DistributedNode):
    def generateInit(self):
        notify_p.info("[DistributedGame] generateInit() in {}".format(self.doId))

class DistributedGameAI(DistributedNodeAI):
    def generate(self, repository = None):
        notify_ai.info("[DistributedGameAI] generate() in {}".format(self.doId))
        notify_ai.info("[DistributedGameAI] location : {}".format(self.getLocation()))
