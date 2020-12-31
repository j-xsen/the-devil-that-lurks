from objects.notifier import Notifier
from direct.task.TaskManagerGlobal import taskMgr
from direct.gui.OnscreenText import OnscreenText
from direct.gui.DirectGui import DirectButton


class SinglePlayer(Notifier):
    def __init__(self, debug_ui):
        Notifier.__init__(self, "ui-single-player")

        self.debug_ui = debug_ui

        taskMgr.doMethodLater(1, self.update_info, "UpdateSinglePlayerInfo")

        self.pid = None

        self.txts = []
        self.btns = []

        # texts
        self.txt_pid = OnscreenText(text="", pos=(1, .8), scale=0.1, fg=(1, 1, 1, 1))
        self.txt_gid = OnscreenText(text="", pos=(1, .7), scale=0.1, fg=(1, 1, 1, 1))

        # texts append
        self.txts.append(self.txt_pid)
        self.txts.append(self.txt_gid)

        # buttons
        self.btn_gid = None

        # buttons append
        self.btns.append(self.btn_gid)

        self.notify.info("[__init__] Created SinglePlayer")

    def change_pid(self, new_pid):
        self.notify.debug(f"[change_pid] Changing PID to {new_pid}")
        self.pid = new_pid
        if new_pid:
            self.txt_pid.text = f"PID: {self.pid}"
        else:
            self.notify.debug(f"[change_pid] No active_connection of PID {new_pid} found!")
            for txt in self.txts:
                txt.text = ""
            for btn in self.btns:
                if btn:
                    btn.destroy()
            self.btns.clear()

    def update_info(self, task):
        self.update_info_manual()
        return task.again

    def update_info_manual(self):
        if self.pid:
            # check if they've disconnected
            if self.pid in self.debug_ui.messager.active_connections.keys():
                # check if they're in a game
                gid = self.debug_ui.messager.active_connections[self.pid].gid
                if gid and not self.btn_gid:
                    self.txt_gid.text = "Game:"
                    self.create_gid_button(gid)
                elif not gid and self.btn_gid:
                    self.txt_gid.text = ""
                    self.btn_gid.destroy()
                    self.btn_gid = None
            else:
                self.change_pid(None)

    def create_gid_button(self, gid):
        self.btn_gid = DirectButton(scale=(0.1, 0.1, 0.1), text=f"{gid}", pos=(1, 1, .6),
                                    frameSize=(-2, 2, -0.75, 0.75),
                                    command=self.debug_ui.change_gid,
                                    extraArgs=[gid])
        self.btns.append(self.btn_gid)
