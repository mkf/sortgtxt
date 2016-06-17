import re

quot = re.compile(r'"([^"]*)"')
msgstrbracke = re.compile('msgstr\[(\d*)]')


def parse_entry(linie):
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
            komenty.append(TransComment(l))
        elif l.startswith("#."):
            komenty.append(ExtraComment(l))
        elif l.startswith("#:"):
            komenty.append(ReferenceComment(l))
        elif l.startswith("#,"):
            komenty.append(FlagsLine(l))
        elif l.startswith("#|"):
            komenty.append(PreviousComment(l))
        elif l.startswith("#~"):
            komenty.append(TildedComment(l))
        elif l.strip() == "#":
            komenty.append(SamHash(l))
        else:
            raise UnknownToken(l)
    if mamyliste:
        return Pluralny(linie, msgid, msgid_plural, msgstrlist, komenty)
    elif msgid == False:
        return Linijki(linie, komenty)
    elif len(msgid) == 0:
        return Metadane(linie, msgstr, komenty)
    else:
        return Wpis(linie, msgid, msgstr, komenty)


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
    if len(bufor) > 0:
        callback(tuple(bufor))


class Baza(object):

    def __init__(self, opened):
        self.wpisy = []
        callbackentries(opened, lambda x: self.wpisy.append(parse_entry(x)))
        for i in range(len(self.wpisy)):
            print(type(self.wpisy[i]))
            if isinstance(self.wpisy[i],Metadane):
                self.metadane = self.wpisy.pop(i)

    def rawzapisdopliku(self, opened):
        self.metadane.rawwrite(opened)
        for wpis in self.wpisy:
            wpis.rawwrite(opened)

    def sortbymsgid(self):
        self.wpisy = sorted(self.wpisy, key=lambda x: x.sortingname())


class Linijki(object):

    def __init__(self, listoflines, komenty):
        self.listoflines = listoflines
        self.komenty = komenty

    def __str__(self):
        return str(self.listoflines) + "\nkomenty:" + str(self.komenty)

    def __repr__(self):
        return str(self)

    def rawwrite(self, opened):
        for line in self.listoflines:
            opened.write(line)
        opened.write("\n")

    def sortingname(self):
        print(self.komenty[0].line)
        return self.komenty[0].line


class Wpis(Linijki):

    def __init__(self, listoflines, msgid, msgstr, komenty):
        self.msgid = msgid
        self.msgstr = msgstr
        for l in listoflines:
            if not l.strip():
                raise PustaLinia
        Linijki.__init__(self, listoflines, komenty)

    def sortingname(self):
        print(self.msgid)
        return self.msgid


class Pluralny(Wpis):

    def __init__(self, listoflines, msgid, msgid_plural, msgstrlist, komenty):
        self.msgid_plural = msgid_plural
        Wpis.__init__(self, listoflines, msgid, msgstrlist, komenty)


class Metadane(Wpis):

    def __init__(self, listoflines, msgstr, komenty):
        Wpis.__init__(self, listoflines, "", msgstr, komenty)


class Comment(object):

    def __init__(self, line):
        self.line = line

    def __str__(self):
        return self.line

    def __repr__(self):
        return self.line


class SamHash(Comment):
    pass


class TransComment(Comment):
    pass


class ExtraComment(Comment):
    pass


class ReferenceComment(Comment):
    pass


class FlagsLine(Comment):
    pass


class PreviousComment(Comment):
    pass


class TildedComment(Comment):
    pass

with open("django.po") as f:
    a = Baza(f)

with open("djangomixed.po") as g:
    b = Baza(g)

with open("docel.po", "w") as tar:
    tar.truncate()
    a.sortbymsgid()
    a.rawzapisdopliku(tar)
    tar.close()

with open("docelmixed.po", "w") as toa:
    toa.truncate()
    b.sortbymsgid()
    b.rawzapisdopliku(toa)
    toa.close()
