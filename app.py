from chatbix import Chatbix
from config import Config
import ui
import urwid

class App:
    def __init__(self, configFile="config.cf"):
        self.config = Config(configFile)
        self.active = True
        self.config = Config(configFile)
        self.config.setConfig("url", "https://chat.chocolytech.info")
        self.config.setConfig("username", "L3nn0x")
        self.chat = Chatbix(self.config.getConfig("url"), self.config.getConfig("username"))
        self.ui = ui.Ui(self)

    def sendMessage(self, content):
        self.chat.sendMessage(content)

    def updateUsers(self):
        self.ui.users.clear()
        for user in sorted(self.chat.users.values(), key=lambda e: e.username):
            data = "o" if user.loggedIn else "x"
            data += " " + user.username
            if user.lastActive != 0:
                data += " (" + user.lastActive.hmsString() + ")"
            self.ui.users.append(urwid.Text(data))

    def update(self, loop, data):
        if self.chat:
            if self.chat.update(self.active):
                self.ui.status.set_text("Connected as " + self.chat.username)
            else:
                self.ui.status.set_text("not connected")
            self.updateUsers()
            channel = self.chat.getChannel("default")
            for message in channel.messages[len(self.ui.main):]:
                self.ui.main.append(urwid.Text(str(message)))
            self.ui.mainWindow.scrollToBottom()
        loop.set_alarm_in(1, self.update)

    def input(self, key):
        pass

    def run(self):
        loop = urwid.MainLoop(self.ui.mainWindow, handle_mouse=False, unhandled_input=self.input)
        loop.set_alarm_in(1, self.update)
        try:
            loop.run()
        except KeyboardInterrupt:
            pass
