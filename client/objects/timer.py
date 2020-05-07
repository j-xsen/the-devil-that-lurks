from direct.gui.OnscreenText import OnscreenText
from direct.task.TaskManagerGlobal import taskMgr, Task
from codes import TIME


class Timer(OnscreenText):
    def __init__(self):
        OnscreenText.__init__(self, text=str(0), pos=(0, 0.75), scale=0.35, fg=(1, 1, 1, 1))
        self.time = TIME

    def start(self):
        self.time = TIME
        self.text = str(self.time)
        taskMgr.doMethodLater(1, self.update, 'Update Timer Object', uponDeath=self.task_stopped)

    def annihilate(self):
        self.stop()
        self.destroy()

    def task_stopped(self, taskdata):
        self.annihilate()

    def stop(self):
        taskMgr.remove('Update Timer Object')

    def update(self, taskdata):
        # if timer = 0, delete task
        if self.time == 1:
            return Task.done
        else:
            self.time -= 1

        self.text = str(self.time)

        return Task.again
