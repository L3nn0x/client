#!/usr/bin/env python3

from app import App

import sys

if len(sys.argv) != 2:
    print("usage", sys.argv[0], "<username>")
    sys.exit(1)

from config import Config

CONFIGFILE = "config.cf"

c = Config(CONFIGFILE)
c.setConfig("username", sys.argv[1])
c.setConfig("url", "https://chat.chocolytech.info")

app = App(CONFIGFILE)
app.run()
