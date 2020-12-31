from direct.showbase.DirectObject import DirectObject
from direct.directnotify.DirectNotifyGlobal import directNotify
from direct.task.TaskManagerGlobal import taskMgr
from direct.gui.OnscreenText import OnscreenText
from direct.gui.DirectGui import DirectButton


class GamesList(DirectObject):
    def __init__(self, debug_ui):
        DirectObject.__init__(self)

        self.notify = directNotify.newCategory("ui-games-list")

        taskMgr.doMethodLater(1, self.update_list, "Update the debug game list")

        self.debug_ui = debug_ui
        self.txt_games_title = OnscreenText(text="Games:", pos=(-1.1, .8), scale=0.1, fg=(1, 1, 1, 1))
        self.btns_games = []
        self.page = 1
        self.max_per_page = 10

        self.accept("arrow_right", self.next_page)
        self.accept("arrow_left", self.previous_page)

        self.update_list_manual()

        self.notify.info("__init__ Created GamesList")

    def update_list(self, task):
        self.update_list_manual()
        return task.again

    def update_list_manual(self):
        # aggressively delete
        for btn in self.btns_games:
            btn.destroy()
            del btn
        self.btns_games.clear()

        all_games_list = sorted(self.debug_ui.messager.games.keys())
        starting_number = (self.page - 1) * self.max_per_page
        ending_number = starting_number + self.max_per_page

        # button appearance
        frame_size = (-2, 2, -.75, 0.75)
        scale = (0.1, 0.1, 0.1)
        pos = (-1.1, 1, 0.65)

        for i in range(starting_number, ending_number):
            if len(all_games_list) > i:
                if i >= starting_number + (self.max_per_page / 2):
                    y_value = 0 - ((i - (starting_number + self.max_per_page / 2)) / 4.5)
                    x_value = 0.5
                else:
                    y_value = 0 - ((i - starting_number) / 4.5)
                    x_value = 0
                new_btn = DirectButton(scale=scale, text=str(all_games_list[i]),
                                       pos=(pos[0] + x_value, pos[1], pos[2] + y_value), frameSize=frame_size,
                                       command=self.game_clicked, extraArgs=[all_games_list[i]])
                self.btns_games.append(new_btn)

    def next_page(self):
        self.page += 1
        self.update_list_manual()

    def previous_page(self):
        if self.page > 1:
            self.page -= 1
            self.update_list_manual()

    def game_clicked(self, gid):
        self.notify.info(f"game_clicked Clicked game {gid}")
        self.debug_ui.change_gid(gid)
        pass
