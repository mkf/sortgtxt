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
                raise UntiedQuote

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


class PustaLinia(Exception):
    pass


class UntiedQuote(Exception):
    pass


class baza(Object):

    def __init__(opened):
        self.wpisy = []


class wpis(Object):

    def __init__(self, listoflines, msgid, msgstr, komenty):
        self.listoflines = listoflines
        self.msgid = msgid
        self.msgstr = msgstr
        for l in linie:
            if len(l) == 0:
                raise PustaLinia


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
