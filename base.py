from direct.showbase.ShowBase import ShowBase
from panda3d.core import *

from direct.distributed.AstronClientRepository import AstronClientRepository

from direct.directnotify.DirectNotify import DirectNotify

from father import Father

version_string = "TDTL-v0"

loadPrcFileData("", "\n".join(["notify-level-local-player info"]))

class MyApp(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)
        ShowBase.set_background_color(self, 0.08, 0.08, 0.08, 1)
        render.setAntialias(AntialiasAttrib.MAuto)
        self.disableMouse()

        self.accept("escape", self.disconnect)

        self.notify = DirectNotify().newCategory("local-player")
        self.player = None

        # Create Repo
        self.repo = AstronClientRepository(dcFileNames = ["astron/distributedclass.dc"],
                                           connectMethod = AstronClientRepository.CM_NET)
        # callback events
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

    def heres_your_player(self, player):
        print("DOES THSI WORK")
        self.notify.info("Received our Player!")
        self.player = player

app = MyApp()

app.run()
