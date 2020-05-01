from direct.showbase.ShowBase import ShowBase
from panda3d.core import *

from direct.distributed.AstronClientRepository import AstronClientRepository

from direct.directnotify.DirectNotify import DirectNotify

from src.father import Father

version_string = "TDTL-v0"

loadPrcFileData("", "\n".join(["notify-level-lp debug"]))

class MyApp(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)
        ShowBase.set_background_color(self, 0.08, 0.08, 0.08, 1)
        render.setAntialias(AntialiasAttrib.MAuto)
        self.disableMouse()

        self.notify = DirectNotify().newCategory("lp")
        self.avatarOV = None

        # Create Repo
        self.repo = AstronClientRepository(dcFileNames = ["astron/distributedclass.dc"],
                                           connectMethod = AstronClientRepository.CM_NET)
        # callback events
        # # controls
        self.accept("escape", self.disconnect)
        self.accept("p", self.ping_games)

        # # server
        self.accept("avatar", self.get_avatar)
        self.accept("distributed_avatar", self.get_distributed_avatar)
        self.accept("receive_game", self.receive_game)
        self.accept("player_count", self.player_count)

        # # magic
        self.accept("CLIENT_HELLO_RESP", self.client_is_handshaked)
        self.accept("CLIENT_EJECT", self.ejected)
        self.accept("LOST_CONNECTION", self.lost_connection)

        # connect
        url = URLSpec()
        url.setServer("127.0.0.1")
        url.setPort(6667)
        self.notify.info("Connecting...")
        self.repo.connect([url],
                          successCallback = self.connection_success,
                          failureCallback = self.connection_failure)
        self.father = None

    def connection_success(self, *args):
        self.notify.info("Connected! Say Hello!")
        self.repo.sendHello(version_string)

    def connection_failure(self):
        self.notify.error("Failed to connect")
        sys.exit()

    def lost_connection(self):
        self.notify.error("Lost connection")
        sys.exit()

    def disconnect(self):
        self.repo.disconnect()
        sys.exit()

    def ejected(self, error_code, reason):
        self.notify.error("Ejected {}: {}".format(error_code, reason))
        sys.exit()

    def client_is_handshaked(self, *args):
        self.notify.info("Thanks! Let's login!")
        self.father = Father()
        login_manager = self.repo.generateGlobalObject(1234, 'DistributedLoginManager')
        # TODO: input name
        login_manager.login("jaxsen")

    def get_avatar(self, avatar):
        self.notify.info("Received our Player!")
        self.avatarOV = avatar
        self.father.set_avatarOV(avatar)

    def get_distributed_avatar(self, avatar):
        self.notify.info("Received DistributedAvatar [()]".format(avatar.doId))

    def receive_game(self):
        self.father.set_game()

    def ping_games(self):
        self.notify.info("Pinging games....")

        if self.avatarOV:
            self.avatarOV.request_game()
            pass
        else:
            self.notify.info("No avatar")

    def player_count(self, count):
        if self.father:
            self.father.player_count(count)

app = MyApp()

app.run()
