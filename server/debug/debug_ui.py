from direct.gui.OnscreenText import OnscreenText
from direct.task.TaskManagerGlobal import taskMgr
from direct.gui.DirectGui import DirectScrolledFrame

class DebugUI:
    def __init__(self, messager):
        taskMgr.doMethodLater(1, self.update_game_list, "Update the debug game list")
        self.txt_title_games = OnscreenText(text="Games:", pos=(-1.1, .8), scale=0.1, fg=(1, 1, 1, 1))
        self.scroll_game = DirectScrolledFrame(canvasSize=(-.4, .4, -2, 2), frameSize=(-.5, .5, -.5, .5),
                                               pos=(-.75, 1, .425))
        self.txt_games = OnscreenText(text="1111", pos=(0, 1.9), scale=0.1, fg=(1, 1, 1, 1),
                                      parent=self.scroll_game.getCanvas())

    def update_game_list(self, task):
        for i in range(0, 50):
            self.txt_games.text += f"{i}\n"
        return task.again
