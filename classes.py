import re

quot = re.compile('"([^"]*)"')
msgstrbracke = re.compile('msgstr\[(\d*)]')


def jakbyco(linie):
    for l in linie:
        if len(l) == 0:
            raise PustaLinia
    k = ""
    komenty = []
    for l in linie:
        if l.startswith('"'):
            if k == "msgid":
                msgid += quot.search(l)
            elif k == "msgid_plural":
                msgid_plural += quot.search(l)
            elif k == "msgstr":
                msgstr += quot.search(l)
            elif k == "msgstr[":
                a = msgstrlist.pop()
                a += quot.search(l)
                msgstrlist.append(a)
            else:
                raise UntiedQuote(l)

        elif l.startswith("msgid "):
            msgid = quot.search(l)
            k = "msgid"
        elif l.startswith("msgid_plural "):
            msgid_plural = quot.search(l)
            k = "msgid_plural"
        elif l.startswith("msgstr "):
            msgstr = quot.search(l)
            k = "msgstr"
        elif l.startswith("msgstr["):
            if not mamyliste:
                mamyliste = true
                msgstrlist = []
            msgstrlist.append((msgstrbracke.search(l), quot.search(l)))
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
        else:
            raise UnknownToken(l)
    if mamyliste:
        return pluralny(linie,msgid,msgid_plural,msgstrlist,komenty)
    elif len(msgid)==0:
        return metadane(linie,msgstr,komenty)
    else:
        return wpis(linie,msgid,msgstr,komenty)


class PustaLinia(Exception):
    pass


class UntiedQuote(UnknownToken):
    pass

class UnknownToken(Exception):
    pass

def callbackentries(opened,callback):
    bufor = []
    for l in opened:
        if len(l)==0:
            if len(bufor)>0:
                callback(tuple(bufor))
                bufor = []
        else:
            bufor.append(l)
    if len(bufor)>0:
        callback(bufor)

class baza(Object):

    def __init__(opened):
        self.wpisy = []
        callbackentries(opened,self.wpisy.append)
        return self


class wpis(Object):

    def __init__(self, listoflines, msgid, msgstr, komenty):
        self.listoflines = listoflines
        self.msgid = msgid
        self.msgstr = msgstr
        for l in linie:
            if len(l) == 0:
                raise PustaLinia
        return self


class pluralny(wpis):

    def __init__(self, listoflines, msgid, msgid_plural, msgstrlist, komenty):
        self.msgid_plural = msgid_plural
        wpis.__init__(self, listoflines, msgid, msgstrlist, komenty)


class metadane(wpis):

    def __init__(self, listoflines, msgstr, komenty):
        wpis.__init__(self, listoflines, "", msgstr, komenty)


class comment(Object):

    def __init__(self, line):
        self.line = line


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

with f as open("django.po"):
    print(baza(f))
