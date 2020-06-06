from direct.gui.DirectGui import OkDialog
from localization.en import LOCAL_EN
from communications.codes import GENERAL

# TODO
#   Create a box
#   Put a message in that box
#   Be able to close the box


class Alert:
    def __init__(self, reason):
        if reason in LOCAL_EN:
            self.dialog = OkDialog(dialogName="OkDialog", text=LOCAL_EN[reason], command=self.destroy)
        else:
            self.dialog = OkDialog(dialogName="OkDialog", text=LOCAL_EN[GENERAL], command=self.destroy)

    def destroy(self, arg):
        self.dialog.cleanup()
        del self.dialog
        del self
