import time
import asyncio
import datetime
from api import ChatbixApi

class Tag:
# Basically, the first two variables shouldn't be modified as they aren't kept by the server
    def __init__(self, tag=0):
        try:
            tag = int(tag)
        except ValueError:
            tag = 0
        self.tag = tag
        # generated by the server
        self.loggedIn = (tag & 1) != 0
        # if this message is generated from another message
        self.generated = (tag & 2) != 0
        # if this message is sent by a bot
        self.bot = (tag & 4) != 0
        # if this message should avoid notifying
        self.noNotif = (tag & 8) != 0
        # 0 -> no change
        # 1-4 -> hidden msg with 4 being 'more' hidden than 1
        # 9-12 -> important msg with 12 being 'more' important than 9
        self.showValue = (tag & 240) >> 4
        # 0 -> plain text
        # 1 -> markdown
        # 2 -> preformatted/code (not trim spaces, use monospace font)
        self.textFormat = (tag & (2**8 | 2**9)) >> 8

    def getTag(self):
        self.tag = self.loggedIn | self.generated << 1 | self.bot << 2 | self.noNotif << 3 | self.showValue << 7 | self.textFormat << 9
        return self.tag
    
    def __str__(self):
        return str(self.getTag())

class Timestamp:
    def __init__(self, timestamp):
        try:
            self.timestamp = int(timestamp)
        except:
            print("Error can't translate the timestamp")
            self.timestamp = 0

    def getDate(self, s="%H:%M:%S"):
        return datetime.datetime.fromtimestamp(self.timestamp).strftime(s)

    def __str__(self):
        return str(self.timestamp)

class Color:
    def __init__(self, color):
        if not color:
            color = "#000000"
        # TODO: convert rgb to hexa
        self.color = color

    def __str__(self):
        return self.color

class User:
    def __init__(self, data):
        self.username = data["username"]
        self.loggedIn = data["logged_in"]
        self.lastActive = Timestamp(data["last_active"])
        self.lastAnswer = Timestamp(data["last_answer"])

class Channel:
    def __init__(self, name):
        self.name = name
        self.messages = []

    def addMessage(self, message):
        self.messages.append(message)

    def __str__(self):
        return self.name

class Message:
    def __init__(self, parent, data):
        self.id = data['id']
        self.author = data['author']
        self.timestamp = Timestamp(data['timestamp'])
        self.content = data['content']
        self.tags = Tag(data['tags'])
        self.color = Color(data['color'])
        self.channel = parent.getChannel(data['channel'])

    def __str__(self):
        return "{} ({}): {}".format(self.author, str(self.timestamp), self.content)

class Chatbix:
    def __init__(self, url, username="Anonymous", loop=None):
        if not loop:
            loop = asyncio.get_event_loop()
        self.loop = loop
        self.api = ChatbixApi(url, loop)
        self.channels = {
                "default" : Channel("default")
                }
        self.users = {}
        self.username = username
        self.authKey = None
        self.lastId = None
        self.color = Color("#000000")

    def getChannel(self, channel):
        if not channel:
            return self.channels["default"]
        try:
            return self.channels[channel]
        except KeyError:
            self.channels[channel] = Channel(channel)
            return self.channels[channel]

    def login(self, password):
        return self.loop.run_until_complete(self.login_async(password))

    async def login_async(self, password):
        if self.authKey:
            return True
        res = await self.api.login_async(self.username, password)
        if len(res) == 0:
            return False
        self.authKey = res
        return True

    def logout(self):
        return self.loop.run_until_complete(self.logout_async())

    async def logout_async(self):
        if not self.authKey:
            return True
        await self.api.logout_async(self.username, self.authKey)
        self.authKey = None
        return True

    def register(self, password):
        return self.loop.run_until_complete(self.register_async(password))

    async def register_async(self, password):
        if self.authKey:
            return True
        res = await self.api.register_async(self.username, password)
        if len(res) == 0:
            return False
        self.authKey = res
        return True

    def update(self, active):
        return self.loop.run_until_complete(self.update_async(active))

    async def update_async(self, active):
        channels = [i for i in self.channels.keys() if i != "default"]
        default = True if "default" in self.channels.keys() else False
        data = await self.api.heartbeat_async(self.username, active=active, authKey=self.authKey, messageId=self.lastId, defaultChannel=default, *channels)
        if len(data) == 0:
            return False
        self.parse(data)
        return True

    def parse(self, data):
        self.parseUsers(data)
        self.parseMessages(data)

    def parseMessages(self, data):
        for msg in data["messages"]:
            m = Message(self, msg)
            m.channel.addMessage(m)

    def parseUsers(self, data):
        self.users = {}
        for user in data["users_connected"]:
            u = User(user)
            self.users[u.username] = u

    def sendMessage(self, content, tag=Tag(), channel=None):
        return self.loop.run_until_complete(self.sendMessage_async(content, tag))

    async def sendMessage_async(self, content, tag=Tag(), channel=None):
        return await self.api.sendMessage_async(self.username, content, color=self.color, tags=tag, channel=channel, authKey=self.authKey)


