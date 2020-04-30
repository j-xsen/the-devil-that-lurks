from direct.showbase.ShowBase import ShowBase
from direct.task import Task
from direct.distributed.PyDatagram import PyDatagram
from direct.distributed.AstronInternalRepository import AstronInternalRepository
from panda3d.core import loadPrcFileData
from time import sleep

from server_globals import *

loadPrcFileData("", "\n".join(["window-type none",
                               "notify-level-ai debug"]))

class ServerAI(ShowBase):
    def __init__(self, server_framerate = 60):
        ShowBase.__init__(self)

        # framerate helpers
        self.server_frametime = 1./server_framerate
        self.taskMgr.add(self.idle, 'idle task', sort = 47)

        # start servers
        self.start_ai_shard()

    def idle(self, task):
        elapsed = globalClock.getDt()
        if elapsed < self.server_frametime:
            sleep(self.server_frametime - elapsed)
        return Task.cont

    def start_ai_shard(self):
        from src.distributed import DistributedMaprootAI

        air = AstronInternalRepository(AIChannel,
                                       serverId = SSChannel,
                                       dcFileNames = ["astron/distributedclass.dc"],
                                       connectMethod = AstronInternalRepository.CM_NET)
        air.connect("127.0.0.1", 7199)
        air.districtId = air.GameGlobalsId = AIChannel

        # create maproot
        maproot = DistributedMaprootAI(air)
        maproot.generateWithRequiredAndId(air.districtId, 0, 1)
        air.setAI(maproot.doId, AIChannel)
        maproot.set_maproot()

server = ServerAI()
server.run()
