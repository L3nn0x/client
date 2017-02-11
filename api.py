import asyncio
import json
import hashlib
from network import Network

class ChatbixApi:
    def __init__(self, url, loop=None):
        if url[-1] != "/":
            url += "/"
        self.url = url + "api/"
        if not loop:
            loop = asyncio.get_event_loop()
        self.loop = loop
        self.net = Network(loop)

    def login(self, username, password):
        return self.loop.run_until_complete(self.login_async(username, password))

    async def login_async(self, username, password, hashFunc=hashlib.sha512):
        password = hashFunc.update(password).digest()
        url = self.url + "login"
        data = {
                "username" : username,
                "password" : password
                }
        ok, token = await self.net.sendData_async(url, data)
        if not ok:
            return ""
        return json.loads(token)["auth_key"]

    def logout(self, username, authKey):
        return self.loop.run_until_complete(self.logout_async(username, authKey))

    async def logout_async(self, username, authKey):
        url = self.url + "logout"
        data = {
                "username" : username,
                "auth_key" : authKey
                }
        return await self.net.sendData_async(url, data)

    def register(self, username, password):
        return self.loop.run_until_complete(self.register_async(username, password))

    async def register_async(self, username, password, hashFunc=hashlib.sha512):
        url = self.url + "register"
        password = hashFunc.update(password).digest()
        data = {
                "username" : username,
                "password" : password
                }
        ok, token = await self.net.sendData_async(url, data)
        if not ok:
            return ""
        return json.loads(token)["auth_key"]

    def heartbeat(self, username, active=True, authKey=None, timestamp=None, messageId=None, defaultChannel=True, *channels):
        return self.loop.run_until_complete(self.heartbeat_async(username, active, authKey, timestamp, messageId, defaultChannel, *channels))

    async def heartbeat_async(self, username, active=True, authKey=None, timestamp=None, messageId=None, defaultChannel=True, *channels):
        url = self.url + "heartbeat"
        params = {
                "username" : username,
                }
        params["active"] = "1" if active else "0"
        if authKey:
            params["authKey"] = str(authKey)
        if timestamp:
            params["timestamp"] = str(timestamp)
        if messageId:
            params["message_id"] = str(messageId)
        if not defaultChannel:
            url += "?no_default_channel"
        if len(channels) > 0:
            params["channels"] = ",".join(channels)
        ok, data = await self.net.getData_async(url, **params)
        if not ok:
            return ""
        return json.loads(data)

    def getMessages(self, timestamp=None, messageId=None, timestampEnd=None, defaultChannel=True, *channels):
        return self.loop.run_until_complete(self.getMessages_async(timestamp, messageId, timestampEnd, defaultChannel, *channels))

    async def getMessages_async(self, timestamp=None, messageId=None, timestampEnd=None, defaultChannel=True, *channels):
        url = self.url + "get_messages"
        params = {}
        if timestamp:
            params["timestamp"] = str(timestamp)
        if messageId:
            params["message_id"] = str(messageId)
        if timestampEnd:
            params["timestamp_end"] = str(timestampEnd)
        if len(channels) > 0:
            params["channels"] = ",".join(channels)
        if not defaultChannel:
            url += "?no_default_channel"
        ok, data = await self.net.getData_async(url, **params)
        if not ok:
            return ""
        return json.loads(data)
    
    def sendMessage(self, username, content, color=None, tags=None, channel=None, authKey=None):
        return self.loop.run_until_complete(self.sendMessage_async(username, content, color, tags, channel, authKey))

    async def sendMessage_async(self, username, content, color=None, tags=None, channel=None, authKey=None):
        url = self.url + "new_message"
        data = {
                "username" : username,
                "content" : content
                }
        if color:
            data["color"] = str(color)
        if tags:
            data["tags"] = str(tags)
        if channel:
            data["channel"] = str(channel)
        if authKey:
            data["auth_key"] = str(authKey)
        return await self.net.sendData_async(url, data)
