from level.level import Level
from direct.actor.Actor import Actor
from direct.gui.DirectGui import DirectButton
from direct.gui.OnscreenText import OnscreenText
from communicator import dg_set_room
from codes import KITCHEN, LIVING_ROOM, BEDROOM, PORCH, DINING_ROOM, TIME
from direct.task.TaskManagerGlobal import taskMgr, Task
from objects.timer import Timer


# Level that all come together during day
class DayLevel(Level):
    def __init__(self, father):
        Level.__init__(self, "Day", "img/egg/mainmenu.egg", father)
        self.positions = [[(-3, 10, -1.5), -145],
                          [(-3, 15, -1.5), -145],
                          [(-3, 20, -1.5), -145],
                          [(-3, 25, -1.5), -145],
                          [(3, 25, -1.5), 145],
                          [(3, 20, -1.5), 145],
                          [(3, 15, -1.5), 145],
                          [(3, 10, -1.5), 145]]

    def create(self):
        # pawns
        pawn_red = Actor("models/egg/pawn",
                         {"breath": "models/egg/pawn-breath"})

        pawn_red.setPos(self.positions[0][0])
        pawn_red.setH(self.positions[0][1])
        pawn_red.setScale(0.75, 0.75, 0.75)
        pawn_red.loop('breath')
        pawn_red.reparentTo(render)

        self.actors.append(pawn_red)

        # buttons on where to go
        btn_kitchen = DirectButton(text="Kitchen", scale=0.1, pos=(0, 0, 0.5),
                                   command=self.set_room, extraArgs=[KITCHEN])
        btn_living_room = DirectButton(text="Living Room", scale=0.1, pos=(0, 0, 0.25),
                                       command=self.set_room, extraArgs=[LIVING_ROOM])
        btn_bedroom = DirectButton(text="Bedroom", scale=0.1, pos=(0, 0, 0),
                                   command=self.set_room, extraArgs=[BEDROOM])
        btn_porch = DirectButton(text="Porch", scale=0.1, pos=(0, 0, -0.25),
                                 command=self.set_room, extraArgs=[PORCH])
        btn_dining_room = DirectButton(text="Dining room", scale=0.1, pos=(0, 0, -0.5),
                                       command=self.set_room, extraArgs=[DINING_ROOM])

        self.buttons.append(btn_kitchen)
        self.buttons.append(btn_living_room)
        self.buttons.append(btn_bedroom)
        self.buttons.append(btn_porch)
        self.buttons.append(btn_dining_room)

        # timer
        self.timer = Timer()
        self.timer.start()

    def set_room(self, room):
        self.father.write(dg_set_room(self.father.pid, room))
