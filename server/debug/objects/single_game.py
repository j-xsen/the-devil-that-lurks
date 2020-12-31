from direct.showbase.DirectObject import DirectObject
from objects.notifier import Notifier
from direct.task.TaskManagerGlobal import taskMgr
from direct.gui.OnscreenText import OnscreenText
from direct.gui.DirectGui import DirectButton

KITCHEN = 212
LIVING_ROOM = 213
BEDROOM = 214
PORCH = 215
DINING_ROOM = 216

ROOMS = {KITCHEN: "Kitchen",
         LIVING_ROOM: "Living Room",
         BEDROOM: "Bedroom",
         PORCH: "Porch",
         DINING_ROOM: "Dining Room",
         0: ""}


class SingleGame(Notifier):
    def __init__(self, messager):
        Notifier.__init__(self, "ui-single-game")

        self.messager = messager

        taskMgr.doMethodLater(1, self.update_info, "Update the debug game info")

        self.gid = None
        self.txt_gid = OnscreenText(text=f"GID: {self.gid}", pos=(1, .8), scale=0.1, fg=(1, 1, 1, 1))
        self.txt_day = OnscreenText(text="", pos=(1, .7), scale=0.08, fg=(1, 1, 1, 1))
        self.txt_red_room = OnscreenText(text="", pos=(1, .6), scale=0.08, fg=(0.68, 0.12, 0.12, 1))

        self.notify.info("[__init__] Created SingleGame")

    def change_gid(self, new_gid):
        self.gid = new_gid
        self.txt_gid.text = f"GID: {self.gid}"

    def update_info(self, task):
        if self.gid in self.messager.games.keys():
            if self.messager.games[self.gid].day:
                self.txt_day.text = "Day"
            else:
                self.txt_day.text = "Night"
            self.txt_day.text += f" {self.messager.games[self.gid].day_count}"
            self.txt_red_room.text = ROOMS[self.messager.games[self.gid].red_room]
        else:
            # GID does not exist
            self.change_gid(None)
            self.txt_day.text = ""
            self.txt_red_room.txt = ""
        return task.cont
