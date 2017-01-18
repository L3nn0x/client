#!/bin/python3

from api import Chat
from app import Application
import sys

if len(sys.argv) < 2:
    print("usage :", sys.argv[0], "nickname [color = #000000]")
    exit(1)

color = "000000"
if len(sys.argv) == 3:
    color = sys.argv[2].lstrip().lstrip('#').rstrip()[:6]
chat = Chat(sys.argv[1], color)

app = Application(chat)
app.run()
