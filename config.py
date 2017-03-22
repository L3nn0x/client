import pickle

class Config:
    def __init__(self, file):
        try:
            f = open(file, "rb")
            self.data = pickle.load(f)
        except Exception:
            self.data = {
                    "url" : "",
                    "username" : "",
                    "color" : ""
                    }
            f = open(file, "wb")
            pickle.dump(self.data, f)
        self.file = file

    def getConfig(self, name):
        if name not in ("url", "username", "color"):
            return ""
        return self.data[name]

    def setConfig(self, name, value):
        if name not in ("url", "username", "color"):
            return
        self.data[name] = value
        with open(self.file, "wb") as f:
            pickle.dump(self.data, f)
