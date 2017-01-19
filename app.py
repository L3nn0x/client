import tkinter as tk
import tkinter.font as Font
from io import BytesIO
from PIL import Image, ImageTk
from hyperlink import HyperlinkManager
import requests
import time
from notifications import NotificationManager

def hmsString(dt):
    h = int(dt / (60 * 60))
    m = int((dt % (60 * 60))/ 60)
    s = int(dt % 60)
    if h > 0:
        return "{}h".format(h)
    if m > 0:
        return "{}m".format(m)
    if s < 10:
        return "<10s"
    return "{}s".format((s // 10) * 10)

class Application:
    def __init__(self, chat):
        self.lastActive = 0
        self.chat = chat
        self.win = tk.Tk()
        self.win.title("chat")
        self.win.protocol("WM_DELETE_WINDOW", self.close)
        self.win.grid_rowconfigure(0, weight=1)
        self.win.grid_columnconfigure(0, weight=1)
        self.outText = tk.Text(self.win)
        self.outText.grid(row=0, sticky=tk.W+tk.E+tk.N+tk.S)
        self.outText.configure(state="disabled")
        self.scrollbar = tk.Scrollbar(self.win)
        self.scrollbar.grid(row=0, column=1,sticky=tk.E+tk.N+tk.S)
        self.scrollbar.config(command=self.outText.yview)
        self.outText.config(yscrollcommand=self.scrollbar.set)
        self.userList = tk.Listbox(self.win)
        self.userList.configure(state="disabled")
        self.userList.grid(row=0, column=2, sticky=tk.W+tk.N+tk.S)
        self.inFrame = tk.Frame(self.win, relief=tk.SUNKEN)
        self.inFrame.grid(row=1, columnspan=3,sticky=tk.N+tk.W+tk.S+tk.E)
        self.inText = tk.Entry(self.inFrame)
        self.inText.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.inText.bind('<Return>', self.send)
        self.sendButton = tk.Button(self.inFrame, command=self.send,text="Send")
        self.sendButton.pack(side=tk.RIGHT)
        self.bold = Font.Font(family="Helvetica", size=14, weight="bold")
        self.bold.configure(weight="bold")
        self.outText.tag_config("AN", font=self.bold)
        self.outText.tag_config("AT", background="blue")
        self.hyperlinkManager = HyperlinkManager(self.outText)
        self.notificationManager = NotificationManager("chat.chocolytech")
        self.users = []
        self.update()
        self.printHelp()
        self.inText.focus()

    def run(self):
        self.win.mainloop()

    def printHelp(self):
        self.outText.configure(state="normal")
        self.outText.insert(tk.END, "\n\n/help to print this message\n/exit to quit\n/nick [nickname] to choose a nickname\n/color [color] to pick a color\n\n")
        self.outText.see(tk.END)
        self.outText.configure(state="disabled")

    def send(self, event=''):
        data = self.inText.get()
        self.inText.delete(0, tk.END)
        if len(data) == 0:
            return
        elif data == "/exit":
            self.close()
        elif data == "/help":
            self.printHelp()
        elif data[:6] == "/nick ":
            self.chat.username = data[6:69]
        elif data[:7] == "/color ":
            self.chat.color = data[7:].rstrip().lstrip().lstrip("#")[:6]
        else:
            self.chat.send(data)

    def update(self):
        if self.win.focus_get() == None:
            self.notificationManager.notifications(True)
            if self.lastActive == 0:
                self.lastActive = time.time()
            elif time.time() - self.lastActive > 10:
                self.chat.isActive(False, self.lastActive)
        else:
            self.notificationManager.notifications(False)
            self.chat.isActive(True)
            self.lastActive = 0
        self.chat.update()
        self.updateUsers()
        if self.chat.diff == 0:
            self.win.after(1000, self.update)
            return
        self.outText.configure(state="normal")
        for msg in self.chat.getDiff():
            self.outText.tag_config(msg.color, foreground="#"+msg.color)
            self.insertMsg(msg)
            if msg.author != self.chat.username:
                self.notificationManager.sendNotification(*self.clean(msg))
        self.outText.see(tk.END)
        self.outText.configure(state="disabled")
        self.win.after(1000, self.update)

    def updateUsers(self):
        users = self.chat.getUsers()
        self.userList.configure(state="normal")
        self.userList.delete(0, tk.END)
        actual = []
        for user in sorted(users, key=lambda e: e.username):
            actual.append(user.username)
            data = user.username
            if user.last_active == 0:
                self.userList.insert(tk.END, data)
            else:
                data += " (" + hmsString(int(time.time() - user.last_active)) + ")"
                self.userList.insert(tk.END, data)
                self.userList.itemconfig(tk.END, fg="gray")
        for user in self.users:
            if user not in actual:
                self.notificationManager.sendNotification(user + " disconnected", "")
        for user in actual:
            if user not in self.users:
                self.notificationManager.sendNotification(user + " connected", "")
        self.users = actual

    def clean(self, msg):
        title = msg.author + " (" + msg.getDate() + ")"
        body = msg.content
        return title, body

    def close(self):
        self.notificationManager.stop()
        self.win.destroy()

    def click(self, link):
        import webbrowser
        webbrowser.open(link, new=2)

    def insertMsg(self, msg):
        tags = []
        if msg.announcement:
            tags.append("AN")
        self.outText.insert(tk.END, msg.author, (msg.color, *tags))
        self.outText.insert(tk.END, " ({}): ".format(msg.getDate()), tags)
        index = msg.content.find("http")
        if index == -1:
            self.outText.insert(tk.END, msg.content+"\n", tags)
        else:
            self.outText.insert(tk.END, msg.content[:index], tags)
            end = msg.content.find(" ", index)
            end = len(msg.content) if end == -1 else end
            self.outText.insert(tk.END, msg.content[index:end], (*tags, *self.hyperlinkManager.add(lambda: self.click(msg.content[index:end]))))
            self.outText.insert(tk.END, " " + msg.content[end:]+"\n", tags)
