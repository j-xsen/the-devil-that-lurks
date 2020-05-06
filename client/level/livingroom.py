from level.level import Level
from direct.actor.Actor import Actor
from chat import Chat


# Level that all come together during day
class LivingRoomLevel(Level):
    def __init__(self, father):
        Level.__init__(self, "Living Room", "img/egg/mainmenu.egg", father)
        self.positions = [[(-3, 10, -1.5), -145],
                          [(-3, 15, -1.5), -145],
                          [(-3, 20, -1.5), -145],
                          [(-3, 25, -1.5), -145],
                          [(3, 25, -1.5), 145],
                          [(3, 20, -1.5), 145],
                          [(3, 15, -1.5), 145],
                          [(3, 10, -1.5), 145]]

    def create(self):
        pawn_red = Actor("models/egg/pawn",
                         {"breath": "models/egg/pawn-breath"})

        pawn_red.setPos(self.positions[0][0])
        pawn_red.setH(self.positions[0][1])
        pawn_red.setScale(0.75, 0.75, 0.75)
        pawn_red.loop('breath')
        pawn_red.reparentTo(render)

        self.actors.append(pawn_red)
        #print(render.ls())
