import sys

from direct.actor.Actor import Actor
from level.level import Level
from panda3d.core import DirectionalLight, PerspectiveLens, Point3, TransparencyAttrib
from direct.gui.DirectGui import OnscreenImage, DirectButton, DGG
from direct.interval.IntervalGlobal import LerpPosHprInterval

class MainMenuLevel(Level):
    def __init__(self, father):
        Level.__init__(self, "Main Menu", "img/egg/mainmenu.egg", father)

        # red pawn
        pawn_red = Actor("models/egg/pawn",
                              {"breath": "models/egg/pawn-breath"})
        pawn_red.setPos(-4, 20, -2)
        pawn_red.setH(-145)
        pawn_red.loop('breath')
        self.actors.append(pawn_red)
        # light
        slight_red = DirectionalLight('slight_red')
        slight_red.setColor((0.682 / 1.5, 0.125 / 1.5, 0.121 / 1.5, 1))
        slight_red.setLens(PerspectiveLens())
        slight_red_np = render.attachNewNode(slight_red)
        self.lights.append(slight_red_np)
        self.lights[0].setPos(10, 15, 10)
        self.lights[0].lookAt(self.actors[0])

        # white pawn
        pawn_white = Actor("models/egg/pawn",
                           {"breath": "models/egg/pawn-breath"})
        pawn_white.setPos(4, 20, -2)
        pawn_white.setH(145)
        pawn_white.loop('breath')
        self.actors.append(pawn_white)
        # light
        dl_white = DirectionalLight('DL White')
        dl_white.setColor((0.9/2.5, 0.9/2.5, 0.9/2.5, 1))
        dl_white.setLens(PerspectiveLens())
        dl_white_np = render.attachNewNode(dl_white)
        self.lights.append(dl_white_np)
        self.lights[1].setPos(-10, 15, 10)
        self.lights[1].lookAt(self.actors[1])

    # for transitions between screens on this level
    # just destroy self.images and self.buttons
    def soft_destroy(self):
        for b in self.buttons:
            self.destroy_button(b)
        for i in self.images:
            self.destroy_image(i)

    def exit_game(self):
        sys.exit()

    def goto_home(self):
        self.soft_destroy()

        LerpPosHprInterval(base.camera, 0.35, Point3(0, 0, 0), Point3(0, 0, 0)).start()

        logo = OnscreenImage(image='img/png/logo.png', pos=(0, 0, 0.625), scale=(1, 1, 0.4))
        logo.setTransparency(TransparencyAttrib.MAlpha)

        exit_button = DirectButton(geom=(self.sprites.find('**/mm-exit-ready'),
                                         self.sprites.find('**/mm-exit-click'),
                                         self.sprites.find('**/mm-exit-hover'),
                                         self.sprites.find('**/mm-exit-disabled')),
                                   relief=None, geom_scale=(0.666, 0, 0.25), geom_pos=(0, 0, -0.75),
                                   command=self.exit_game)
        settings_button = DirectButton(geom=(self.sprites.find('**/mm-settings-ready'),
                                             self.sprites.find('**/mm-settings-click'),
                                             self.sprites.find('**/mm-settings-hover'),
                                             self.sprites.find('**/mm-settings-disabled')),
                                       relief=None, geom_scale=(0.666, 0, 0.25), geom_pos=(0, 0, -0.4),
                                       command=self.goto_settings)
        play_button = DirectButton(geom=(self.sprites.find('**/mm-play-ready'),
                                         self.sprites.find('**/mm-play-click'),
                                         self.sprites.find('**/mm-play-hover'),
                                         self.sprites.find('**/mm-play-disabled')),
                                   relief=None, geom_scale=(1, 0, 0.3), geom_pos=(0, 0, 0.1), command=self.goto_singleplayer)

        self.images.append(logo)
        self.buttons.append(exit_button)
        self.buttons.append(settings_button)
        self.buttons.append(play_button)

    def goto_settings(self):
        self.soft_destroy()

        LerpPosHprInterval(base.camera, 0.35, Point3(1, 12, 0), Point3(-7, 0, 0)).start()

        settings_image = OnscreenImage(image='img/png/mm-settings-ready.png', pos=(0, 0, 0.7), scale=(0.5, 1, 0.2))
        settings_image.setTransparency(TransparencyAttrib.MAlpha)

        back_button = DirectButton(geom=(self.sprites.find('**/mm-back-ready'),
                                         self.sprites.find('**/mm-back-click'),
                                         self.sprites.find('**/mm-back-hover'),
                                         self.sprites.find('**/mm-back-disabled')),
                                   relief=None, geom_scale=(0.666, 0, 0.25), geom_pos=(0, 0, -0.75),
                                   command=self.goto_home)

        self.buttons.append(back_button)
        self.images.append(settings_image)

    def goto_singleplayer(self):
        self.father.set_active_level("Game")

    def goto_play(self):
        self.soft_destroy()
        LerpPosHprInterval(base.camera, 0.35, Point3(-1, 12, 0), Point3(7, 0, 0)).start()

        play_image = OnscreenImage(image='img/png/mm-play-ready.png', pos=(0, 0, 0.7), scale=(0.5, 1, 0.2))
        play_image.setTransparency(TransparencyAttrib.MAlpha)

        singleplayer_button = DirectButton(geom=(self.sprites.find('**/mm-singleplayer-ready'),
                                                 self.sprites.find('**/mm-singleplayer-click'),
                                                 self.sprites.find('**/mm-singleplayer-hover'),
                                                 self.sprites.find('**/mm-singleplayer-disabled')),
                                           relief=None, geom_scale=(0.9, 0, 0.2), geom_pos=(0, 0, 0.2),
                                           command=self.goto_singleplayer)
        multiplayer_button = DirectButton(geom=(self.sprites.find('**/mm-multiplayer-ready'),
                                                self.sprites.find('**/mm-multiplayer-click'),
                                                self.sprites.find('**/mm-multiplayer-hover'),
                                                self.sprites.find('**/mm-multiplayer-disabled')),
                                          relief=None, geom_scale=(0.9, 0, 0.2), geom_pos=(0, 0, -0.3),
                                          command=self.goto_home, state=DGG.DISABLED)
        back_button = DirectButton(geom=(self.sprites.find('**/mm-back-ready'),
                                         self.sprites.find('**/mm-back-click'),
                                         self.sprites.find('**/mm-back-hover'),
                                         self.sprites.find('**/mm-back-disabled')),
                                   relief=None, geom_scale=(0.666, 0, 0.25), geom_pos=(0, 0, -0.75),
                                   command=self.goto_home)

        self.buttons.append(singleplayer_button)
        self.buttons.append(multiplayer_button)
        self.buttons.append(back_button)

        self.images.append(play_image)

    def create(self):
        # upon creation, enable these items
        self.actors[0].reparentTo(render)
        self.actors[0].setLight(self.lights[0])
        self.actors[1].reparentTo(render)
        self.actors[1].setLight(self.lights[1])

        self.goto_home()
