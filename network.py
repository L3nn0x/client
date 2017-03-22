import requests

class Network:
    def getData(self, url, **params):
        r = requests.get(url, data=params)
        if r.status_code != 200:
            return False, r.status_code
        return True, r.text

    def sendData(self, url, data):
        r = requests.post(url, json=data)
        if r.status_code != 200:
            return False, r.status_code
        return True, r.text

