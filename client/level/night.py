from level.level import Level
from direct.actor.Actor import Actor
from direct.gui.OnscreenText import OnscreenText
from direct.gui.DirectGui import DirectCheckButton
from objects.timer import Timer
from communications.datagrams import dg_set_kill
from panda3d.core import DirectionalLight, PerspectiveLens, Point3, TransparencyAttrib
from objects.clickable import Clickable


class NightLevel(Level):

    multifiles = ""

    def __init__(self, level_holder):
        Level.__init__(self, "Night", self.multifiles, level_holder)
        self.players_here = 0

    def create(self):
        Level.create(self)

        pawn_red = Clickable(self.level_holder, "art/pawns/pawn.bam", "actor_pawn_red")
        pawn_red.setPos(-4,20,-2)
        pawn_red.setH(-145)
        pawn_red.loop('breath')
        self.clickables["actor_pawn_red"] = pawn_red
        self.clickables["actor_pawn_red"].reparentTo(render)

        """pawn_red = Actor("pawns/pawn.bam")
        pawn_red.setPos(-4, 20, -2)
        pawn_red.setH(-145)
        pawn_red.loop('breath')
        self.actors["actor_pawn_red"] = pawn_red
        # red pawn light
        dlight_red = DirectionalLight('DL Red')
        dlight_red.setColor((0.682 / 1.5, 0.125 / 1.5, 0.121 / 1.5, 1))
        dlight_red.setLens(PerspectiveLens())
        dlight_red_np = render.attachNewNode(dlight_red)
        self.lights["dlight_red_np"] = dlight_red_np
        self.lights["dlight_red_np"].setPos(10, 15, 10)
        self.lights["dlight_red_np"].lookAt(self.actors["actor_pawn_red"])

        self.actors["actor_pawn_red"].reparentTo(render)
        self.actors["actor_pawn_red"].setLight(self.lights["dlight_red_np"])"""
