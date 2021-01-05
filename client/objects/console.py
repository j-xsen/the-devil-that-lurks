from objects.entry import Entry
from direct.showbase.DirectObject import DirectObject
from objects.notifier import Notifier
from direct.gui.OnscreenText import OnscreenText
from panda3d.core import TextNode


class Console(Entry, DirectObject, Notifier):
    def __init__(self, level_holder):
        DirectObject.__init__(self)
        Entry.__init__(self, "", (-1.25, 1, -.9), self.entered_command, focus=True, sort_order=1500)
        Notifier.__init__(self, "console")

        self.level_holder = level_holder

        self.accept("arrow_up", self.move_command, extraArgs=[1])
        self.accept("arrow_down", self.move_command, extraArgs=[0])

        self.logs = []
        self.archivable = []
        self.pos = -1

    def destroy(self):
        for log in self.logs:
            log.destroy()
        Entry.destroy(self)

    def pressed_tilda(self):
        self.notify.debug("[pressed_tilda] Destroy console")
        self.destroy()

    def entered_command(self, text):
        self.notify.debug(f"[entered_command] Ran command `{text}` in console")
        split = text.split()
        success = False

        if split[0] in self.mapping:
            success = self.mapping[split[0]](self, split[1:])
        else:
            self.notify.warning(f"[entered_command] Unknown command: {text}")

        self.entry["focus"] = True
        if success is not None:
            if type(success) == bool:
                self.add_to_log(text, success)
            elif type(success) == list:
                self.add_to_log_multiple(success)

    def add_to_log(self, text, valid, archivable=True):
        """
        Add a message (text) to the log
        @param text: The text to add to the log
        @type text: str
        @param valid: Was the command valid?
        @type valid: bool
        @param archivable: Should the log be able to be retrieved through arrow keys?
        @type archivable: bool
        """
        self.notify.debug(f"[add_to_log] Adding {text} to log!")
        if len(text) > 0:
            for log in self.logs:
                log.move_up()
            new_log = ConsoleLog(text, valid)
            self.logs.insert(0, new_log)

            if archivable:
                self.archivable.insert(0, self.logs[0])

    def add_to_log_multiple(self, log_list):
        """
        @param log_list: List of logs to add
        @type log_list: list
        """
        for log in log_list:
            for existing_log in self.logs:
                existing_log.move_up()
            log.create()
            self.logs.insert(0, log)
            if self.logs[0].archivable:
                self.archivable.insert(0, self.logs[0])

    def move_command(self, direction):
        """
        Bring up command history
        @param direction: Which direction to move in the log. Up = 1, Down = 0
        @type direction: int
        """
        if len(self.archivable) > 0:
            if direction == 1:
                if len(self.archivable) > self.pos + 1:
                    self.pos += 1
            else:
                if self.pos > -1:
                    self.pos -= 1

            if self.pos > -1:
                self.entry.enterText(self.archivable[self.pos].text)
            else:
                self.entry.set("")

    # COMMANDS
    def debug(self, args):
        return True

    def exit_game(self, args):
        self.level_holder.exit_game()
        return True

    def change_level(self, args):
        error_log = None
        success = False
        if len(args) == 1:
            value = None
            # see if args[0] can be turned into an int
            try:
                value = int(args[0])
            except ValueError:
                self.notify.debug(f"[change_level] Cannot convert {args[0]} into integer!")
                error_log = ConsoleLog(f"Invalid argument: {args[0]}", False, archivable=False,
                                       auto_create=False)

            if value is not None:
                # check if its a level
                if value in self.level_holder.levels:
                    self.notify.debug(f"[change_level] Changing level to {self.level_holder.levels[value]}")
                    self.level_holder.set_active_level(value)
                    success = True
                else:
                    self.notify.debug(f"[change_level] Non-existent level: {args[0]}")
                    error_log = ConsoleLog(f"Non-existent level: {args[0]}", False, archivable=False,
                                           auto_create=False)
        else:
            self.notify.debug(f"[change_level] Invalid number of args! ({len(args)})")
            error_log = ConsoleLog(f"Invalid number of arguments! Required: 1, Submitted: {len(args)}",
                                   False, archivable=False, auto_create=False)
        if success:
            return True
        else:
            args_string = ""
            for arg in args:
                args_string += f" {arg}"

            return [ConsoleLog(f"level{args_string}", False, auto_create=False), error_log]

    def clear(self, args):
        for log in self.logs:
            log.destroy()
        self.logs.clear()
        return None

    def print_logs(self, args):
        """
        Print self.logs
        """
        string = ""
        for log in self.logs:
            string += f"{log.text}, "
        return [ConsoleLog(f"logs", True, auto_create=False),
                ConsoleLog(string, True, archivable=False, auto_create=False)]

    def print_archivable(self, args):
        """
        Print self.archivable
        """
        string = ""
        for log in self.archivable:
            string += f"{log.text}, "
        string = string[:-2]
        return [ConsoleLog(f"archivable", True, auto_create=False),
                ConsoleLog(string, True, archivable=False, auto_create=False)]

    def print_active_level(self, args):
        """
        Print the LevelHolder's active level
        """
        active_level = self.level_holder.active_level
        level_name = self.level_holder.levels[self.level_holder.active_level]
        return [ConsoleLog(f"active_level", True, auto_create=False),
                ConsoleLog(f"{level_name.name} ({active_level})", True, archivable=False,
                           auto_create=False)]

    def print_levels(self, args):
        """
        Print all levels in LevelHolder
        """
        string = ""
        for level in self.level_holder.levels:
            string += f"{self.level_holder.levels[level].name}: {level}, "
        string = string[:-2]
        return [ConsoleLog(f"levels", True, auto_create=False),
                ConsoleLog(string, True, archivable=False, auto_create=False)]

    def print_commands(self, args):
        """
        Print all commands
        """
        string = ""
        for command in self.mapping.keys():
            string += f"{command}, "
        string = string[:-2]
        return [ConsoleLog(f"commands", True, auto_create=False),
                ConsoleLog(string, True, archivable=False, auto_create=False)]

    mapping = {
        "commands": print_commands,
        "exit": exit_game,
        "level": change_level,
        "levels": print_levels,
        "test": debug,
        "clear": clear,
        "logs": print_logs,
        "archivable": print_archivable,
        "active_level": print_active_level
    }


class ConsoleLog:
    def __init__(self, text, valid, archivable=True, auto_create=True):
        """
        @param text: What did they type in the console?
        @type text: str
        @param valid: Did the command work?
        @type valid: bool
        @param archivable: Should the log be retrievable via arrow keys?
        @type archivable: bool
        @param auto_create: Should the text of the log be auto created?
        @type auto_create: bool
        """
        self.text = text
        self.valid = valid
        self.log = None
        self.archivable = archivable
        if auto_create:
            self.create()

        if not valid and self.log is not None:
            self.log["fg"] = (1, 0, 0, 1)

    def create(self):
        self.log = OnscreenText(text=self.text, fg=(1, 1, 1, 1), pos=(-1.25, -.8),
                                align=TextNode.ALeft)

        if not self.archivable:
            self.log["pos"] = (self.log["pos"][0] + 0.05, self.log["pos"][1])
            self.log["fg"] = (.8, .8, .8, 1)

        if not self.valid:
            self.log["fg"] = (1, 0, 0, 1)

            if not self.archivable:
                self.log["fg"] = (.8, 0, 0, 1)

    def move_up(self):
        """
        Move the OnscreenText up
        """
        self.log.setPos(self.log.getPos()[0], self.log.getPos()[1] + 0.07)

    def destroy(self):
        self.log.destroy()
