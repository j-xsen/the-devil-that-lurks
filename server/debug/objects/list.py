from direct.task.TaskManagerGlobal import taskMgr
from direct.gui.DirectGui import DirectButton
from direct.gui.OnscreenText import OnscreenText


class List:
    def __init__(self, the_dict, max_per_page, pos, scale=(0.1, 0.1, 0.1), frame_size=(-2, 2, -0.75, 0.75),
                 command=None, active=True):
        """
        :param the_dict: The dictionary to create a list of
        :type the_dict: dict
        :param max_per_page: Maximum number of items per page
        :type max_per_page: int
        :param pos: The position that you want the buttons to appear
        :type pos: tuple
        :param scale: The scale of the buttons
        :type scale: tuple
        :param frame_size: The size of the buttons
        :type frame_size: tuple
        :param command: The command to run if a command is desired. If none is inputted, it'll make OnscreenTexts
                        rather than DirectButton
        :type command: function
        :param active: Should the list be displayed?
        :type active: bool
        """
        taskMgr.doMethodLater(1, self.update_list, "Update the list")

        self.active = active
        self.page = 1
        self.max_per_page = max_per_page
        self.frame_size = frame_size
        self.scale = scale
        self.pos = pos
        self.command = command

        self.the_dict = the_dict
        self.btns = []

    def clear_buttons(self):
        """
        Gets rid of all the visual aspects of the list
        """
        for btn in self.btns:
            btn.destroy()
            del btn
        self.btns.clear()

    def change_active(self, new_active):
        """
        Use this to change self.active
        :param new_active: The new self.active value
        :type new_active: bool
        """
        self.active = new_active
        if new_active:
            self.update_list_manual()
        else:
            self.clear_buttons()

    def update_list(self, task):
        """
        Don't call this. If you need to update list, use update_list_manual()
        """
        if self.active:
            self.update_list_manual()
        return task.again

    def update_list_manual(self):
        """
        Manually update the list
        """
        self.clear_buttons()

        sorted_dict = sorted(self.the_dict)
        starting_number = (self.page - 1) * self.max_per_page
        ending_number = starting_number + self.max_per_page

        for i in range(starting_number, ending_number):
            if len(sorted_dict) > i:
                if i >= starting_number + (self.max_per_page / 2):
                    y_value = 0 - ((i - (starting_number + self.max_per_page / 2)) / 4.5)
                    x_value = 0.5
                else:
                    y_value = 0 - ((i - starting_number) / 4.5)
                    x_value = 0
                if self.command:
                    new_btn = DirectButton(scale=self.scale, text=str(sorted_dict[i]),
                                           pos=(self.pos[0] + x_value, 1, self.pos[1] + y_value),
                                           frameSize=self.frame_size, command=self.command,
                                           extraArgs=[sorted_dict[i]])
                else:
                    new_btn = OnscreenText(text=f"{sorted_dict[i]}", pos=(self.pos[0] + x_value,
                                                                          self.pos[1] + y_value),
                                           scale=0.1, fg=(1, 1, 1, 1))
                self.btns.append(new_btn)

    def next_page(self):
        """
        Go to the next page. Hook this up to however you want to change it."
        """
        if self.active:
            self.page += 1
            self.update_list_manual()

    def previous_page(self):
        """
        Go to the previous page. Hook this up to however you want to change it.
        """
        if self.page > 1 and self.active:
            self.page -= 1
            self.update_list_manual()
