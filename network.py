import asyncio
import aiohttp

class Network:
    def __init__(self, loop=None):
        if not loop:
            loop = asyncio.get_event_loop()
        self.loop = loop
        self.session = aiohttp.ClientSession(loop=loop)

    async def getData_async(self, url, **params):
        async with self.session.get(url, params=params) as resp:
            if resp.status != 200:
                return False, resp.status
            return True, await resp.text()

    async def sendData_async(self, url, data):
        res = await self.session.post(url, data=json.dumps(data))
        if res.status != 200:
            return False, res.status
        return True, await res.text()

    def getData(self, url, **params):
        return self.loop.run_until_complete(self.getData_async(url, **params))

    def sendData(self, url, data):
        return self.loop.run_until_complete(self.sendData_async(url, data))


