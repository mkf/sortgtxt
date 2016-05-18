import re

quot = re.compile('"([^"]*)"')
msgstrbracke = re.compile('msgstr\[(\d*)]')


def jakbyco(linie):
    for l in linie:
        if not l.strip():
            raise PustaLinia
    k = ""
    komenty = []
    mamyliste = False
    msgid = False
    for l in linie:
        if l.startswith('"'):
            if k == "msgid":
                msgid += quot.search(l).group(0)
            elif k == "msgid_plural":
                msgid_plural += quot.search(l).group(0)
            elif k == "msgstr":
                msgstr += quot.search(l).group(0)
            elif k == "msgstr[":
                a = msgstrlist.pop()
                a += quot.search(l).group(0)
                msgstrlist.append(a)
            else:
                raise UntiedQuote(l)

        elif l.startswith("msgid "):
            msgid = quot.search(l).group(0)
            k = "msgid"
        elif l.startswith("msgid_plural "):
            msgid_plural = quot.search(l).group(0)
            k = "msgid_plural"
        elif l.startswith("msgstr "):
            msgstr = quot.search(l).group(0)
            k = "msgstr"
        elif l.startswith("msgstr["):
            if not mamyliste:
                mamyliste = True
                msgstrlist = []
            msgstrlist.append((msgstrbracke.search(
                l).group(0), quot.search(l).group(0)))
            k = "msgstr["
        elif l.startswith("# "):
            komenty.append(transcomme(l))
        elif l.startswith("#."):
            komenty.append(extracomme(l))
        elif l.startswith("#:"):
            komenty.append(refere(l))
        elif l.startswith("#,"):
            komenty.append(flagsline(l))
        elif l.startswith("#|"):
            komenty.append(previouscomme(l))
        elif l.startswith("#~"):
            komenty.append(tilded(l))
        elif l.strip() == "#":
            komenty.append(samhash(l))
        else:
            raise UnknownToken(l)
    if mamyliste:
        return pluralny(linie, msgid, msgid_plural, msgstrlist, komenty)
    elif msgid == False:
        return linijki(linie, komenty)
    elif len(msgid) == 0:
        return metadane(linie, msgstr, komenty)
    else:
        return wpis(linie, msgid, msgstr, komenty)


class PustaLinia(Exception):
    pass


class UnknownToken(Exception):
    pass


class UntiedQuote(UnknownToken):
    pass


def callbackentries(opened, callback):
    bufor = []
    for l in opened:
        if not l.strip():
            if len(bufor) > 0:
                callback(tuple(bufor))
                bufor = []
        else:
            bufor.append(l)
            print(l)
    if len(bufor) > 0:
        callback(tuple(bufor))


class baza(object):

    def __init__(self, opened):
        self.wpisy = []
        callbackentries(opened, lambda x: self.wpisy.append(jakbyco(x)))


class linijki(object):

    def __init__(self, listoflines, komenty):
        self.listoflines = listoflines
        self.komenty = komenty

    def __str__(self):
        return str(self.listoflines) + "\nkomenty:" + str(self.komenty)

    def __repr__(self):
        return str(self)


class wpis(linijki):

    def __init__(self, listoflines, msgid, msgstr, komenty):
        self.msgid = msgid
        self.msgstr = msgstr
        for l in listoflines:
            if not l.strip():
                raise PustaLinia
        linijki.__init__(self, listoflines, komenty)


class pluralny(wpis):

    def __init__(self, listoflines, msgid, msgid_plural, msgstrlist, komenty):
        self.msgid_plural = msgid_plural
        wpis.__init__(self, listoflines, msgid, msgstrlist, komenty)


class metadane(wpis):

    def __init__(self, listoflines, msgstr, komenty):
        wpis.__init__(self, listoflines, "", msgstr, komenty)


class comment(object):

    def __init__(self, line):
        self.line = line

    def __str__(self):
        return self.line

    def __repr__(self):
        return self.line


class samhash(comment):
    pass


class transcomme(comment):
    pass


class extracomme(comment):
    pass


class refere(comment):
    pass


class flagsline(comment):
    pass


class previouscomme(comment):
    pass


class tilded(comment):
    pass

with open("django.po") as f:
    print(baza(f).wpisy)
