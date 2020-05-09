from direct.directnotify.DirectNotifyGlobal import directNotify
from direct.gui.DirectGui import DirectFrame
from direct.gui.DirectGui import OkDialog

from localization import LOCAL_ENGLISH
from codes import GENERAL

# TODO
#   Create a box
#   Put a message in that box
#   Be able to close the box


class Alert:
    def __init__(self, reason):
        if reason in LOCAL_ENGLISH:
            self.dialog = OkDialog(dialogName="OkDialog", text=LOCAL_ENGLISH[reason], command=self.destroy)
        else:
            self.dialog = OkDialog(dialogName="OkDialog", text=LOCAL_ENGLISH[GENERAL])

    def destroy(self, arg):
        self.dialog.cleanup()
        del self.dialog
        del self
