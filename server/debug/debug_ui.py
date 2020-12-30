from direct.gui.OnscreenText import OnscreenText
from direct.task.TaskManagerGlobal import taskMgr
from direct.gui.DirectGui import DirectButton
from direct.showbase.DirectObject import DirectObject
from direct.directnotify.DirectNotifyGlobal import directNotify


class DebugUI(DirectObject):

    def __init__(self, messager):
        DirectObject.__init__(self)

        self.notify = directNotify.newCategory("ui")
        self.notify.debug("__init__ Created DebugUI")

        taskMgr.doMethodLater(1, self.games_update_list, "Update the debug game list")
        self.txt_games_title = OnscreenText(text="Games:", pos=(-1.1, .8), scale=0.1, fg=(1, 1, 1, 1))
        self.btns_games = []

        self.debug_games_list = {}
        for i in range(1, 50):
            self.debug_games_list[i] = f"test_{i}"

        self.game_page = 1
        self.game_max_per_page = 10

        self.games_update_list_manual()

        self.accept("arrow_right", self.games_next_page)
        self.accept("arrow_left", self.games_previous_page)

    def games_update_list(self, task):
        self.games_update_list_manual()
        return task.again

    def games_update_list_manual(self):
        # aggressively delete
        for btn in self.btns_games:
            btn.destroy()
            del btn
        self.btns_games.clear()

        all_games_list = sorted(self.debug_games_list.keys())
        starting_number = (self.game_page - 1) * self.game_max_per_page
        ending_number = starting_number + self.game_max_per_page

        # button appearance
        frame_size = (-2, 2, -.75, 0.75)
        scale = (0.1, 0.1, 0.1)
        pos = (-1.1, 1, 0.65)

        for i in range(starting_number, ending_number):
            if len(all_games_list) > i:
                if i >= starting_number + (self.game_max_per_page / 2):
                    y_value = 0 - ((i - (starting_number + self.game_max_per_page / 2)) / 4.5)
                    x_value = 0.5
                else:
                    y_value = 0 - ((i - starting_number) / 4.5)
                    x_value = 0
                new_btn = DirectButton(scale=scale, text=str(all_games_list[i]),
                                       pos=(pos[0] + x_value, pos[1], pos[2] + y_value), frameSize=frame_size,
                                       command=self.games_game_clicked, extraArgs=[all_games_list[i]])
                self.btns_games.append(new_btn)

    def games_next_page(self):
        self.game_page += 1
        self.games_update_list_manual()

    def games_previous_page(self):
        if self.game_page > 1:
            self.game_page -= 1
            self.games_update_list_manual()

    def games_game_clicked(self, gid):
        print(f"games_game_clicked Clicked game {gid}")
        pass
