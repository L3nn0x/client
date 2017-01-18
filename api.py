import requests
import time
import json
import datetime

class Message:
    def __init__(self, data):
        self.id = int(data["id"])
        self.timestamp = (data["timestamp"])
        self.author = data["author"].split("#")[0]
        if len(data["author"].split("#")) > 1 and len(data["author"].split("#")[1]) > 1:
            self.color = data["author"].split("#")[1]
        else:
            self.color = "000000"
        self.content = data["content"]
        self.announcement = False if data["announcement"] == 0 else True
    
    def getDate(self):
        return datetime.datetime.fromtimestamp(self.timestamp).strftime("%H:%M:%S")

    def __str__(self):
        return "{} ({}): {}".format(self.author, self.getDate(), self.content)

class User:
    def __init__(self, username, data):
        self.username = username
        self.last_active = data["last_active"]

class Chat:
    def __init__(self, username, color="000000"):
        self.username = username
        self.color = color
        self.beat = 0
        self.link = "https://chat.chocolytech.info/api.php"
        self.getLink = "?heartbeat={}&username={}&active={}"
        self.diff = 0
        self.history = []
        self.connected = {}

    def update(self):
        data = requests.get(self.link + self.getLink.format(self.beat, self.username, time.time()))
        if data.status_code != 200:
            return False
        diff = len(self.history)
        data = json.loads(data.text)
        for user, d in data["connected"].items():
            self.connected[user] = User(user, d)
        for msg in data["messages"]:
            self.history.append(Message(msg))
        self.beat = self.history[-1].id
        self.diff = len(self.history) - diff
        return True

    def getDiff(self):
        return self.history[len(self.history) - self.diff:]

    def send(self, msg):
        headers = {"Content-Type" : "application/json", "charset" : "utf-8"}
        data = {'username' : self.username + "#" + self.color, 'content' : msg}
        r = requests.post(self.link, data = json.dumps(data), headers = headers)
        return False if r.status_code != 200 else True


