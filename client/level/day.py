from level.level import Level
from direct.actor.Actor import Actor
from panda3d.core import DirectionalLight, PerspectiveLens
from direct.gui.DirectGui import DirectButton
from direct.gui.OnscreenText import OnscreenText
from communicator import dg_set_room
from codes import KITCHEN, LIVING_ROOM, BEDROOM, PORCH, DINING_ROOM
from objects.timer import Timer
from panda3d.core import TextNode


# Level that all come together during day
class DayLevel(Level):
    def __init__(self, father):
        Level.__init__(self, "Day", "img/egg/mainmenu.egg", father)
        self.positions = [[(-3, 10, -1.5), -145],
                          [(-3, 15, -1.5), -145],
                          [(-3, 20, -1.5), -145],
                          [(-3, 25, -1.5), -145],
                          [(0, 30, -1.5), 180],
                          [(3, 25, -1.5), 145],
                          [(3, 20, -1.5), 145],
                          [(3, 15, -1.5), 145],
                          [(3, 10, -1.5), 145]]

    def create(self):
        # white light
        dl_white = DirectionalLight('DL White')
        dl_white.setColor((0.9 / 2.5, 0.9 / 2.5, 0.9 / 2.5, 1))
        dl_white.setLens(PerspectiveLens())
        dl_white_np = render.attachNewNode(dl_white)
        dl_white_np.setPos(-10, 15, 10)
        self.lights.append(dl_white_np)

        # red light
        dl_red = DirectionalLight('DL Red')
        dl_red.setColor((0.682 / 1.5, 0.125 / 1.5, 0.121 / 1.5, 1))
        dl_red.setLens(PerspectiveLens())
        dl_red_np = render.attachNewNode(dl_red)
        dl_red_np.setPos(10, 15, 10)
        self.lights.append(dl_red_np)

        for p in self.father.players:
            # pawns
            pawn_red = Actor("models/egg/pawn",
                             {"breath": "models/egg/pawn-breath"})

            pos = self.positions[list(self.father.players).index(p)]

            pawn_red.setPos(pos[0])
            pawn_red.setH(pos[1])
            pawn_red.setScale(0.75, 0.75, 0.75)
            pawn_red.loop('breath')
            pawn_red.reparentTo(render)

            if p in self.father.dead:
                pawn_red.setLight(dl_red_np)
            else:
                pawn_red.setLight(dl_white_np)

            self.actors.append(pawn_red)

            # name tag
            name_tag = TextNode("Name tag for {}".format(p))
            name_tag.setText(self.father.players[p]["name"])
            name_tag.setAlign(TextNode.ACenter)
            name_tag.setTextColor(0.682, 0.125, 0.121, 1)
            node_path = render.attachNewNode(name_tag)
            node_path.setHpr(0, 0, 0)
            node_path.setScale(0.5)
            node_path.setPos(pos[0][0], pos[0][1] + 1.5, pos[0][2] + 3)
            node_path.setBin('fixed', 0)
            self.text_nodepaths.append(node_path)

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

        # day count
        txt_day = OnscreenText(text="Day: {}".format(self.father.day), pos=(0.75, 0.75), scale=0.2, fg=(1, 1, 1, 1))

        self.text.append(txt_day)

        # timer
        self.timer = Timer()
        self.timer.start()

    def set_room(self, room):
        self.father.write(dg_set_room(self.father.pid, room))
