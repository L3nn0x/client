from urwid import *

class ExtendedListBox(ListBox):
    __metaclass__ = MetaSignals
    signals = ["setAutoScroll"]

    def setAutoScroll(self, switch):
        if type(switch) != bool:
            return
        self._autoScroll = switch
        emit_signal(self, "setAutoScroll", switch)

    autoScroll = property(lambda s: s._autoScroll, setAutoScroll)

    def __init__(self, body):
        super().__init__(body)
        self.autoScroll = True

    def switchBody(self, body):
        if self.body:
            disconnect_signal(body, "modified", self._invalidate)
        self.body = body
        self._invalidate()
        connect_signal(body, "modified", self._invalidate)

    def keypress(self, size, key):
        super().keypress(size, key)
        if key in ("page up", "page down"):
            if self.get_focus()[1] == len(self.body) - 1:
                self.autoScroll = True
            else:
                self.autoScroll = False

    def scrollToBottom(self):
        if self.autoScroll:
            self.set_focus(len(self.body) - 1)

class MainEdit(Edit):
    def __init__(self, parent):
        self.parent = parent
        super().__init__()

    def keypress(self, size, key):
        super().keypress(size, key)
        if key in ("page up", "page down"):
            self.parent.mainList.keypress(size, key)
        elif key in ("ctrl d", "ctrl c"):
            raise ExitMainLoop()
        elif key == "enter":
            self.parent.parent.sendMessage(self.get_edit_text())
            self.set_edit_text("")

class Menu(WidgetPlaceholder):
    def __init__(self, parent):
        super().__init__(Text("menu/channels placeholder"))
        self.parent = parent

class MainWindow(Frame):
    def __init__(self, parent):
        self.parent = parent
        self.menu = Menu(self)
        self.edit = MainEdit(self)
        self.status = Text("not connected", align='right')
        header = Columns([('weight', 3, self.menu), ('weight', 1, self.status)], focus_column=0)
        self.chat = SimpleListWalker([])
        self.mainList = ExtendedListBox(self.chat)
        self.users = SimpleListWalker([])
        users = ListBox(self.users)
        win = Frame(Columns([('weight', 3, LineBox(self.mainList)), ('weight', 1, LineBox(users, title="Users"))], dividechars=0))
        super().__init__(win, header=header, footer=LineBox(self.edit), focus_part='footer')

    def scrollToBottom(self):
        self.mainList.scrollToBottom()

class Ui:
    def __init__(self, parent):
        self.mainWindow = MainWindow(parent)
        self.menu = self.mainWindow.menu
        self.edit = self.mainWindow.edit
        self.status = self.mainWindow.status
        self.users = self.mainWindow.users
        self.main = self.mainWindow.chat
