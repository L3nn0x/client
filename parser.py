class Token:
    def __init__(self, begin, end, formated, token):
        self.begin = begin
        self.end = end
        self.formated = formated
        self.token = token

    def __str__(self):
        return "{} {} {}".format(self.begin, self.end, self.formated)

class Parser:
    def __init__(self, toFind=""):
        self.toFind = toFind

    def parse(self, msg, stopChar=" "):
        res = []
        for char in self.toFind:
            i = -1
            while True:
                i = msg.find(char, i + 1)
                if i == -1:
                    break
                tmp = msg[i:].split(stopChar)
                if len(tmp) < 1:
                    break
                if len(tmp[0]) <= len(char):
                    continue
                res.append(Token(i, i + len(tmp[0]) - 1, tmp[0], char))
                i += len(tmp[0]) - 1
        res = sorted(res, key=lambda e: e.begin)
        r = []
        i = 0
        j = 1
        if len(res) == 1:
            return res
        while i < len(res):
            if res[i].end <= res[j].begin:
                r.append(res[i])
                i = j
                j += 1
            else:
                j += 1
            if j >= len(res):
                r.append(res[i])
                break
        return r

