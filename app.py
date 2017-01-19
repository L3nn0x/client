import tkinter as tk
import tkinter.font as Font
from io import BytesIO
from PIL import Image, ImageTk
from hyperlink import HyperlinkManager
import requests
import time
import subprocess

def sendNotification(msgs):
    if len(msgs) > 3:
        authors = set()
        for msg in msgs:
            authors.add(msg.author)
        author = " " + authors.pop()
        if len(authors) > 1:
            author = ""
        subprocess.run(["notify-send", "-a", "chat.chocolytech", "new messages" + author, str(len(msgs)) + " new messages"])
    else:
        for msg in msgs:
            subprocess.run(["notify-send", "-a", "chat.chocolytech", "new message from " + msg.author, str(msg)])

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
        self.inText = tk.Entry(self.win)
        self.inText.grid(row=1, sticky=tk.S+tk.W+tk.E)
        self.inText.bind('<Return>', self.send)
        self.sendButton = tk.Button(command=self.send,text="Send")
        self.sendButton.grid(row=1, sticky=tk.E)
        self.bold = Font.Font(family="Helvetica", size=14, weight="bold")
        self.bold.configure(weight="bold")
        self.outText.tag_config("AN", font=self.bold)
        self.outText.tag_config("AT", background="blue")
        self.hyperlinkManager = HyperlinkManager(self.outText)
        self.notifications = False
        self.update()
        self.printHelp()
        self.inText.focus()
        self.notifications = True

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
            if self.lastActive == 0:
                self.lastActive = time.time()
            elif time.time() - self.lastActive > 10:
                self.chat.isActive(False, self.lastActive)
        else:
            self.chat.isActive(True)
            self.lastActive = 0
        self.chat.update()
        if self.chat.diff == 0:
            self.win.after(1000, self.update)
            return
        self.outText.configure(state="normal")
        for msg in self.chat.getDiff():
            self.outText.tag_config(msg.color, foreground="#"+msg.color)
            self.insertMsg(msg)
        if not self.win.focus_get() and self.notifications:
            sendNotification(self.chat.getDiff())
        self.outText.see(tk.END)
        self.outText.configure(state="disabled")
        self.win.after(1000, self.update)

    def close(self):
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
