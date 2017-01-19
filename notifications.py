import subprocess
import time
from threading import Thread

class NotificationManager(Thread):
    def __init__(self, name, displayTime=5, updateTime=3, sizeMax=64):
        super().__init__()
        self.name = name
        self.displayTime = displayTime
        self.updateTime = updateTime
        self.sizeMax = sizeMax
        self.notifs = []
        self.isRunning = True
        self.active = True
        super().start()

    def stop(self):
        self.isRunning = False
        self.join()

    def notifications(self, active):
        self.active = active

    def run(self):
        while self.isRunning:
            if self.active:
                self._send()
            self.notifs = []
            time.sleep(self.updateTime)

    def sendNotification(self, title, body):
        self.notifs.append((title, body))

    def _send(self):
        process = ["notify-send", "-a", self.name, "-u", "normal", "-t", str(self.displayTime*1000)]
        if len(self.notifs) > 3:
            process.append(str(len(self.notifs)) + " new messages")
            subprocess.run(process)
        else:
            for msg in self.notifs:
                process = ["notify-send", "-a", self.name, "-u", "normal", "-t", str(self.displayTime*1000)]
                process.append(msg[0])
                sub = msg[1][:self.sizeMax]
                if len(sub) < len(msg[1]):
                    sub += "..."
                process.append(sub)
                subprocess.run(process)
