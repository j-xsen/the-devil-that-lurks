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
    def generate(self):
        notify_p.info("[DistributedMaproot] generate() in {}".format(self.doId))

class DistributedMaprootAI(DistributedObjectAI):
    def generate(self):
        notify_ai.info("[DistributedMaprootAI] generate() in {}".format(self.doId))
        self.games_available = []

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

    def any_games(self, client):
        notify_ai.info("[DistributedMaprootAI] any_games() for {} in {}".format(client, self.doId))
        if len(self.games_available) == 0:
            notify_ai.info("[DistributedMaprootAI] No games found. Make one.")
            self.create_game(client)
        else:
            for g in self.games_available:
                self.send_client_game(client, g)
                break

    def create_game(self, client):
        notify_ai.info("[DistributedMaprootAI] create_game() for {} in {}".format(client, self.doId))
        # create the game
        game = DistributedGameAI(self.air)
        game.generateWithRequiredAndId(self.air.allocateChannel(), self.doId,
                                       0)  # random doId, parentId, zoneId
        game.setAI(self.air.ourChannel)

        # Give client interest
        self.air.clientAddInterest(client, 0, game.getDoId(), 1)  # client, interest, parent, zone

        # Append it
        self.games_available.append(game.doId)

        self.send_client_game(client, game.doId)

    def send_client_game(self, client, game):
        # send it to client
        client_do = self.air.doId2do[client]
        client_do.sendUpdate("receive_game", [game])

        # add client
        game_do = self.air.doId2do[game]
        game_do.add_player(client)

    def game_started(self, game):
        if game in self.games_available:
            self.games_available.remove(game)


class DistributedMaprootUD(DistributedObjectUD):
    def generate(self):
        notify_ud.info("[DistributedMaprootUD] generate() in {}".format(self.doId))

    def create_avatar(self, clientId):
        notify_ud.info("[DistributedMaprootUD] create_avatar({}) in {}".format(clientId, self.doId))
        self.sendUpdate("createAvatar", [clientId])

# # # Distributed Avatar
class DistributedAvatar(DistributedObject):
    def generateInit(self):
        notify_p.info("[DistributedAvatar] generateInit() in {}".format(self.doId))
        base.messenger.send("distributed_avatar", [self])

    def receive_game(self, game):
        notify_p.info("[DistributedAvatar] receive_game({}) in {}".format(game, self.doId))
        base.messenger.send("receive_game")

class DistributedAvatarOV(DistributedObjectOV):
    def generateInit(self):
        notify_p.info("[DistributedAvatarOV] generateInit() in {}".format(self.doId))

        # make yourself known to client
        base.messenger.send("avatar", [self])

    def request_game(self):
        notify_p.info("[DistributedAvatarOV] request_game() in {}".format(self.doId))
        self.sendUpdate("request_game")

    def receive_game(self, game):
        notify_p.info("[DistributedAvatarOV] receive_game({}) in {}".format(game, self.doId))
        base.messenger.send("receive_game")

    def player_count(self, count):
        notify_p.info("[DistributedAvatarOV] playerCount({}) in {}".format(count, self.doId))
        base.messenger.send("player_count", [count])

class DistributedAvatarAI(DistributedObjectAI):
    def generate(self, repository = None):
        notify_ai.info("[DistributedAvatarAI] generate() in {}".format(self.doId))
        self.game = None

    def request_game(self):
        notify_ai.info("[DistributedAvatarAI] request_game() in {}".format(self.doId))

        # check if open game
        maproot = self.air.doId2do[self.getLocation()[0]]
        maproot.any_games(self.doId)

# # # DistributedGame

class DistributedGame(DistributedObject):
    def generateInit(self):
        notify_p.info("[DistributedGame] generateInit() in {}".format(self.doId))

class DistributedGameAI(DistributedObjectAI):
    def generate(self, repository = None):
        notify_ai.info("[DistributedGameAI] generate() in {}".format(self.doId))
        # notify_ai.info("[DistributedGameAI] location : {}".format(self.getLocation()))
        self.players = []

    def add_player(self, client):
        notify_ai.info("[DistributedGameAI] add_player({}) in {}".format(client, self.doId))
        self.players.append(client)

        for p in self.players:
            client_do = self.air.doId2do[p]
            client_do.sendUpdate("player_count", [len(self.players)])
