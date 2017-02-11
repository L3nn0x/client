from chatbix import Chatbix
import asyncio
import sys
import signal

URL = "https://chat.chocolytech.info"
USER = "L3nn0x"

loop = asyncio.get_event_loop()

chat = Chatbix(URL, USER, loop=loop)

last = 0

async def update():
    global last
    while True:
        await chat.update_async(True)
        for msg in chat.channels["default"].messages:
            if msg.id <= last:
                continue
            print(msg)
            last = msg.id
        await asyncio.sleep(1)

def userInput():
    asyncio.ensure_future(chat.sendMessage_async(sys.stdin.readline()))

def signalHandler(signal, frame):
    loop.stop()
    sys.exit(0)

signal.signal(signal.SIGINT, signalHandler)

loop.add_reader(sys.stdin, userInput)
asyncio.ensure_future(update())
loop.run_forever()
