from direct.showbase.ShowBase import ShowBase
from direct.task import Task
from direct.distributed.AstronInternalRepository import AstronInternalRepository
from direct.directnotify.DirectNotifyGlobal import directNotify
from panda3d.core import loadPrcFileData
from time import sleep

from server_globals import LoginManagerId, UDChannel, SSChannel

loadPrcFileData("", "\n".join(["window-type none",
                               "notify-level-ud debug"]))
notify = directNotify.newCategory("udserver")

class ServerUD(ShowBase):
    def __init__(self, server_framerate = 60):
        ShowBase.__init__(self)

        # prevent 100% cpu
        self.server_frametime = 1./server_framerate
        self.taskMgr.add(self.idle, 'idle task', sort = 47)

        self.startUberDOG()

    def idle(self, task):
        elapsed = globalClock.getDt()
        if elapsed < self.server_frametime:
            sleep(self.server_frametime - elapsed)
        return Task.cont

    def startUberDOG(self):
        notify.info("Starting UberDOG")

        # UberDOG Repository
        air = AstronInternalRepository(UDChannel,
                                       serverId = SSChannel,
                                       dcFileNames = ["astron/distributedclass.dc"],
                                       dcSuffix = "UD",
                                       connectMethod = AstronInternalRepository.CM_NET)
        air.connect("127.0.0.1", 7199)
        air.districtId = air.GameGlobalsId = UDChannel

        # Create Login Manager
        self.login_manager = air.generateGlobalObject(LoginManagerId, 'DistributedLoginManager')

server = ServerUD()
server.run()