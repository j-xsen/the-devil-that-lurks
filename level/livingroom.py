from level.level import Level
from direct.actor.Actor import Actor
from panda3d.core import *
from game.chat import Chat

# Level that all come together during day
class LivingRoomLevel(Level):
    def __init__(self, father):
        Level.__init__(self, "Game", "img/egg/mainmenu.egg", father)
        self.positions = [[(-3, 10, -1.5), -145],
                          [(-3, 15, -1.5), -145],
                          [(-3, 20, -1.5), -145],
                          [(-3, 25, -1.5), -145],
                          [(3, 25, -1.5), 145],
                          [(3, 20, -1.5), 145],
                          [(3, 15, -1.5), 145],
                          [(3, 10, -1.5), 145]]

    def create(self):
        for p in self.father.players:
            pawn_red = Actor("models/egg/pawn",
                             {"breath": "models/egg/pawn-breath"})
            if p.local_player:
                pawn_red.setPos(-0, 30, -1.5)
                pawn_red.setH(-180)
            else:
                if p.number > self.father.get_local_player().get_number():
                    pawn_red.setPos(self.positions[p.get_number() - 1][0])
                    pawn_red.setH(self.positions[p.get_number() - 1][1])
                else:
                    pawn_red.setPos(self.positions[p.get_number()][0])
                    pawn_red.setH(self.positions[p.get_number()][1])
            pawn_red.setScale(0.75, 0.75, 0.75)
            pawn_red.loop('breath')
            pawn_red.reparentTo(render)
            p.set_pos(pawn_red.getPos())

            self.text_nodepaths.append(Chat(p.get_pos(), "Hello"))
            self.actors.append(pawn_red)
        #print(render.ls())
