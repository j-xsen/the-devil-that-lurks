from level.level import Level
from direct.actor.Actor import Actor
from panda3d.core import DirectionalLight, PerspectiveLens
from direct.gui.DirectGui import DirectButton
from direct.gui.OnscreenText import OnscreenText
from communications.datagrams import dg_set_room
from communications.codes import KITCHEN, LIVING_ROOM, BEDROOM, PORCH, DINING_ROOM, ROOMS
from objects.timer import Timer
from panda3d.core import TextNode
from panda3d.core import VirtualFileSystem, Filename


# Level that all come together during day
class DayLevel(Level):

    multifiles = [""]

    def __init__(self, level_holder):
        Level.__init__(self, "Day", self.multifiles, level_holder)
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
        Level.create(self)

        scale_normal = (0.75, 1, 0.25)
        scale_long = (1.25, 1, 0.3)

        VirtualFileSystem.getGlobalPtr().mount(Filename("mf/room-buttons.mf"), ".",
                                               VirtualFileSystem.MFReadOnly)
        egg = loader.loadModel("room-buttons/room-buttons.egg")

        # white light
        dlight_white = DirectionalLight('DL White')
        dlight_white.setColor((0.9 / 2.5, 0.9 / 2.5, 0.9 / 2.5, 1))
        dlight_white.setLens(PerspectiveLens())
        dlight_white_np = render.attachNewNode(dlight_white)
        dlight_white_np.setPos(-10, 15, 10)
        self.lights["dlight_white_np"] = dlight_white_np

        # red light
        dlight_red = DirectionalLight('DL Red')
        dlight_red.setColor((0.682 / 1.5, 0.125 / 1.5, 0.121 / 1.5, 1))
        dlight_red.setLens(PerspectiveLens())
        dlight_red_np = render.attachNewNode(dlight_red)
        dlight_red_np.setPos(10, 15, 10)
        self.lights["dlight_red_np"] = dlight_red_np

        for p in self.level_holder.players:
            # pawns
            pawn_red = Actor("pawns/pawn.bam")

            pos = self.positions[list(self.level_holder.players).index(p)]

            pawn_red.setPos(pos[0])
            pawn_red.setH(pos[1])
            pawn_red.setScale(0.75, 0.75, 0.75)
            pawn_red.loop('breath')
            pawn_red.reparentTo(render)

            if not self.level_holder.players[p].alive:
                pawn_red.setLight(dlight_red_np)
            else:
                pawn_red.setLight(dlight_white_np)

            self.actors["actor_pawn_red_{}".format(p)] = pawn_red

            # name tag
            name_tag = TextNode("name_tag_for_{}".format(p))
            name_tag.setText(self.level_holder.players[p].name)
            name_tag.setAlign(TextNode.ACenter)
            name_tag.setTextColor(0.682, 0.125, 0.121, 1)
            node_path = render.attachNewNode(name_tag)
            node_path.setHpr(0, 0, 0)
            node_path.setScale(0.5)
            node_path.setPos(pos[0][0], pos[0][1] + 1.5, pos[0][2] + 3)
            node_path.setBin('fixed', 0)
            self.text_nodepaths["name_tag_for_{}".format(p)] = node_path

        # buttons on where to go
        if self.level_holder.red_room == KITCHEN:
            btn_kitchen = DirectButton(scale=scale_normal, pos=(0, 0, 0.5),
                                       command=self.set_room, extraArgs=[KITCHEN],
                                       geom=(egg.find('**/room-kitchen-redroom'),
                                             egg.find('**/room-kitchen-click'),
                                             egg.find('**/room-kitchen-hover'),
                                             egg.find('**/room-kitchen-click')), relief=None)
        else:
            btn_kitchen = DirectButton(scale=scale_normal, pos=(0, 0, 0.5),
                                       command=self.set_room, extraArgs=[KITCHEN],
                                       geom=(egg.find('**/room-kitchen-ready'),
                                             egg.find('**/room-kitchen-click'),
                                             egg.find('**/room-kitchen-hover'),
                                             egg.find('**/room-kitchen-click')), relief=None)
        if self.level_holder.red_room == LIVING_ROOM:
            btn_living_room = DirectButton(scale=scale_long, pos=(0, 0, 0.25),
                                           command=self.set_room, extraArgs=[LIVING_ROOM],
                                           geom=(egg.find('**/room-livingroom-redroom'),
                                                 egg.find('**/room-livingroom-click'),
                                                 egg.find('**/room-livingroom-hover'),
                                                 egg.find('**/room-livingroom-click')), relief=None)
        else:
            btn_living_room = DirectButton(scale=scale_long, pos=(0, 0, 0.25),
                                           command=self.set_room, extraArgs=[LIVING_ROOM],
                                           geom=(egg.find('**/room-livingroom-ready'),
                                                 egg.find('**/room-livingroom-click'),
                                                 egg.find('**/room-livingroom-hover'),
                                                 egg.find('**/room-livingroom-click')), relief=None)
        if self.level_holder.red_room == BEDROOM:
            btn_bedroom = DirectButton(scale=scale_normal, pos=(0, 0, 0),
                                       command=self.set_room, extraArgs=[BEDROOM],
                                       geom=(egg.find('**/room-bedroom-redroom'),
                                             egg.find('**/room-bedroom-click'),
                                             egg.find('**/room-bedroom-hover'),
                                             egg.find('**/room-bedroom-click')), relief=None)
        else:
            btn_bedroom = DirectButton(scale=scale_normal, pos=(0, 0, 0),
                                       command=self.set_room, extraArgs=[BEDROOM],
                                       geom=(egg.find('**/room-bedroom-ready'),
                                             egg.find('**/room-bedroom-click'),
                                             egg.find('**/room-bedroom-hover'),
                                             egg.find('**/room-bedroom-click')), relief=None)
        if self.level_holder.red_room == PORCH:
            btn_porch = DirectButton(scale=scale_normal, pos=(0, 0, -0.25),
                                     command=self.set_room, extraArgs=[PORCH],
                                     geom=(egg.find('**/room-porch-redroom'),
                                           egg.find('**/room-porch-click'),
                                           egg.find('**/room-porch-hover'),
                                           egg.find('**/room-porch-click')), relief=None)
        else:
            btn_porch = DirectButton(scale=scale_normal, pos=(0, 0, -0.25),
                                     command=self.set_room, extraArgs=[PORCH],
                                     geom=(egg.find('**/room-porch-ready'),
                                           egg.find('**/room-porch-click'),
                                           egg.find('**/room-porch-hover'),
                                           egg.find('**/room-porch-click')), relief=None)
        if self.level_holder.red_room == DINING_ROOM:
            btn_dining_room = DirectButton(scale=scale_long, pos=(0, 0, -0.5),
                                           command=self.set_room, extraArgs=[DINING_ROOM],
                                           geom=(egg.find('**/room-diningroom-redroom'),
                                                 egg.find('**/room-diningroom-click'),
                                                 egg.find('**/room-diningroom-hover'),
                                                 egg.find('**/room-diningroom-click')), relief=None)
        else:
            btn_dining_room = DirectButton(scale=scale_long, pos=(0, 0, -0.5),
                                           command=self.set_room, extraArgs=[DINING_ROOM],
                                           geom=(egg.find('**/room-diningroom-ready'),
                                                 egg.find('**/room-diningroom-click'),
                                                 egg.find('**/room-diningroom-hover'),
                                                 egg.find('**/room-diningroom-click')), relief=None)

        self.gui["btn_kitchen"] = btn_kitchen
        self.gui["btn_living_room"] = btn_living_room
        self.gui["btn_bedroom"] = btn_bedroom
        self.gui["btn_porch"] = btn_porch
        self.gui["btn_dining_room"] = btn_dining_room

        # day count
        txt_day_number = OnscreenText(text="Day: {}".format(self.level_holder.day), pos=(-0.75, 0.75),
                                      scale=0.2, fg=(1, 1, 1, 1))

        self.text["txt_day_number"] = txt_day_number

        # timer
        self.timer = Timer(0)

    def set_room(self, room):
        self.messager.write(dg_set_room(self.messager.pid, room))
