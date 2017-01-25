from api import Chat
import time
import recastai
import feedparser

TOKEN = "6ead7aca030ceed70e2a9836a73dbdf3"

class Rss:
    def __init__(self, link):
        self.link = link
        parse = feedparser.parse(self.link)
        try:
            a = parse["version"]
            self.title = parse.feed.title
            self.subtitle = parse.feed.subtitle
            self.printLink = parse.feed.link
            self.error = None
        except KeyError:
            self.error = parse["bozo_exception"]

    def __str__(self):
        return self.title + " - " + self.subtitle

    def getLatest(self, number):
        try:
            parse = feedparser.parse(self.link)
            response = self.title + ":\n>"
            for entry in parse["entries"][:number]:
                response += entry.title + ": " + entry.link + "\n"
            return response
        except KeyError:
            return "Error while loading " + self.title + ": " + parse["bozo_exception"]

class Conv:
    def __init__(self, name, token):
        self.name = name
        self.token = token
        self.rss = {}

chat = Chat("bot")

client = recastai.Client(TOKEN, "en")

convTokens = {}

chat.update()

while True:
    chat.update()
    for msg in chat.getDiff():
        if "@bot" in msg.content:
            r = None
            try:
                conv = convTokens[msg.author]
                r = client.text_converse(msg.content, conversation_token=conv.token)
            except KeyError:
                r = client.text_converse(msg.content)
                convTokens[msg.author] = Conv(msg.author, r.conversation_token)
            reply = r.reply()
            if r.action and r.action.done and r.action.slug == "add_rss":
                conv = convTokens[msg.author]
                tmp = r.get_memory('rss')
                tmp = Rss(tmp.raw)
                if tmp.error:
                    reply = tmp.error
                else:
                    conv.rss[tmp.link] = tmp
            elif r.action and r.action.done and r.action.slug == "list_rss":
                conv = convTokens[msg.author]
                reply += " " + "\n".join(list(conv.rss))
            elif r.action and r.action.done and r.action.slug == "news":
                conv = convTokens[msg.author]
                reply += "\n" + "\n".join(i.getLatest(1) for _, i in conv.rss.items())
            chat.send(reply)
    time.sleep(1)
