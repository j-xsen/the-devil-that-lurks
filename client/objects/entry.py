from direct.gui.DirectGui import DirectEntry
from direct.showbase.DirectObject import DirectObject


class Entry(DirectObject):
    def __init__(self, placeholder, pos, on_enter):
        """
        Object of a simple entry field
        @param placeholder: text to appear in textbox automatically
        @type placeholder: string
        @param pos: where to place the textbox
        @type pos: (int, int, int)
        @param on_enter: function to call upon them submitting a response
        @type on_enter: function
        """
        DirectObject.__init__(self)
        self.accept('mouse1', self.click_out)
        self.placeholder = placeholder
        self.on_enter = on_enter
        self.entry = DirectEntry(initialText=self.placeholder, scale=0.05, focus=0,
                                 focusOutCommand=self.focus_out,
                                 focusInCommand=self.focus_in,
                                 pos=pos)

    def focus_out(self):
        if self.entry.get() == "":
            self.entry.enterText(self.placeholder)
        else:
            # they typed Something.
            # TODO validate
            self.on_enter(self.entry.get())

    def focus_in(self):
        self.entry.set("")

    def click_out(self):
        self.entry.setFocus()

    def destroy(self):
        self.entry.destroy()
        self.ignoreAll()
