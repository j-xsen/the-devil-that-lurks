from level.level import Level
from direct.actor.Actor import Actor
from direct.gui.OnscreenText import OnscreenText
from direct.gui.DirectGui import DirectCheckButton
from objects.timer import Timer
from communications.datagrams import dg_set_kill


# Level that all come together during day
class NightLevel(Level):

    multifiles = []

    def __init__(self, father):
        Level.__init__(self, "Night", self.multifiles, father)
        self.players_here = 0

    def create(self):
        Level.create(self)

        pawn_red = Actor("pawns/pawn.bam")
        pawn_red.setPos(-4, 20, -2)
        pawn_red.setH(-145)
        pawn_red.loop('breath')
        self.actors["actor_pawn_red"] = pawn_red
