import tkinter as tk
import tkinter.font as Font
from io import BytesIO
from PIL import Image, ImageTk
from hyperlink import HyperlinkManager
import requests

class Application:
    def __init__(self, chat):
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
        self.hyperlinkManager = HyperlinkManager(self.outText)
        self.update()
        self.inText.focus()

    def run(self):
        self.win.mainloop()

    def send(self, event=''):
        data = self.inText.get()
        self.inText.delete(0, tk.END)
        if len(data) == 0:
            return
        elif data == "/exit":
            self.close()
            return
        self.chat.send(data)

    def update(self):
        self.chat.update()
        if self.chat.diff == 0:
            self.win.after(1000, self.update)
            return
        self.outText.configure(state="normal")
        for msg in self.chat.getDiff():
            self.outText.tag_config(msg.color, foreground="#"+msg.color)
            self.insertMsg(msg)
        self.outText.see(tk.END)
        self.outText.configure(state="disabled")
        self.win.after(1000, self.update)

    def close(self):
        self.win.destroy()

    def click(self, link):
        self.window = tk.Toplevel(self.win)
        self.window.maxsize(width=300, height=300)
        self.cv = tk.Canvas(self.window)
        self.window.bind('<Button-1>', lambda e: self.window.destroy())
        self.cv.pack(side='top', fill='both', expand='yes')
        try:
            r = requests.get(link)
            if r.status_code != 200:
                print(r.status_code)
            self.image = ImageTk.PhotoImage(Image.open(BytesIO(r.content)))
            self.cv.create_image(10, 10, image=self.image)
        except Exception as e:
            print(e)

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