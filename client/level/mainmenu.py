from direct.actor.Actor import Actor
from level.level import Level
from panda3d.core import DirectionalLight, PerspectiveLens, Point3, TransparencyAttrib
from direct.gui.DirectGui import OnscreenImage, DirectButton, DGG
from direct.interval.IntervalGlobal import LerpPosHprInterval
from objects.alert import Alert

from communications.datagrams import dg_request_game


class MainMenuLevel(Level):

    multifiles = ["mainmenu.mf"]

    def __init__(self, father):
        Level.__init__(self, "Main Menu", self.multifiles, father)

    # for transitions between screens on this level
    # just destroy self.images and self.buttons
    def soft_destroy(self):
        """
        Destroys GUI & Images, but saves Lights and Actors
        @return:
        @rtype:
        """
        for g in self.gui:
            self.gui[g].destroy()
        for i in self.images:
            self.images[i].destroy()

    def goto_home(self):
        self.soft_destroy()

        LerpPosHprInterval(base.camera, 0.35, Point3(0, 0, 0), Point3(0, 0, 0)).start()

        logo = OnscreenImage(image=loader.loadTexture('mainmenu/logo.png'), pos=(0, 0, 0.625),
                             scale=(1, 1, 0.4))
        logo.setTransparency(TransparencyAttrib.MAlpha)

        exit_button = DirectButton(geom=(self.sprites.find('**/mm-exit-ready'),
                                         self.sprites.find('**/mm-exit-click'),
                                         self.sprites.find('**/mm-exit-hover'),
                                         self.sprites.find('**/mm-exit-disabled')),
                                   relief=None, geom_scale=(0.666, 0, 0.25), geom_pos=(0, 0, -0.75),
                                   command=self.father.exit_game)
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
                                   relief=None, geom_scale=(1, 0, 0.3), geom_pos=(0, 0, 0.1),
                                   command=self.goto_play)

        if not self.father.check_connection():
            play_button["state"] = DGG.DISABLED

        self.images["img_logo"] = logo
        self.gui["btn_exit"] = exit_button
        self.gui["btn_settings"] = settings_button
        self.gui["btn_play"] = play_button

    def goto_settings(self):
        self.soft_destroy()

        LerpPosHprInterval(base.camera, 0.35, Point3(1, 12, 0), Point3(-7, 0, 0)).start()

        settings_image = OnscreenImage(image='mainmenu/mm-settings-ready.png', pos=(0, 0, 0.7),
                                       scale=(0.5, 1, 0.2))
        settings_image.setTransparency(TransparencyAttrib.MAlpha)

        back_button = DirectButton(geom=(self.sprites.find('**/mm-back-ready'),
                                         self.sprites.find('**/mm-back-click'),
                                         self.sprites.find('**/mm-back-hover'),
                                         self.sprites.find('**/mm-back-disabled')),
                                   relief=None, geom_scale=(0.666, 0, 0.25), geom_pos=(0, 0, -0.75),
                                   command=self.goto_home)

        self.gui["btn_settings_back"] = back_button
        self.images["img_settings"] = settings_image

    def goto_play(self):
        if self.father.my_connection:
            self.father.write(dg_request_game(self.father.pid))
        else:
            Alert(-2)
            self.failed_to_connect()

    def failed_to_connect(self):
        """
        Called when Father is told that we failed to connect.
        Disables the play button since there's Nothing to connect to
        """
        self.gui["btn_play"]["state"] = DGG.DISABLED

    def connected(self):
        """
        Called when Father is told that we've been connected
        Enables the play button
        """
        self.gui["btn_play"]["state"] = DGG.NORMAL

    def create(self):
        Level.create(self)

        # reset game vars when going to main menu
        self.father.reset_game_vars()

        self.sprites = loader.loadModel("mainmenu/mainmenu.egg")
        # red pawn
        pawn_red = Actor("pawns/pawn.bam")
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

        # white pawn
        pawn_white = Actor("pawns/pawn.bam")
        pawn_white.setPos(4, 20, -2)
        pawn_white.setH(145)
        pawn_white.loop('breath')
        self.actors["actor_pawn_white"] = pawn_white
        # light
        dlight_white = DirectionalLight('DL White')
        dlight_white.setColor((0.9 / 2.5, 0.9 / 2.5, 0.9 / 2.5, 1))
        dlight_white.setLens(PerspectiveLens())
        dlight_white_np = render.attachNewNode(dlight_white)
        self.lights["dlight_white_np"] = dlight_white_np
        self.lights["dlight_white_np"].setPos(-10, 15, 10)
        self.lights["dlight_white_np"].lookAt(self.actors["actor_pawn_white"])

        # upon creation, enable these items
        self.actors["actor_pawn_red"].reparentTo(render)
        self.actors["actor_pawn_red"].setLight(self.lights["dlight_red_np"])
        self.actors["actor_pawn_white"].reparentTo(render)
        self.actors["actor_pawn_white"].setLight(self.lights["dlight_white_np"])

        self.goto_home()
