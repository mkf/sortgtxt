import re

quot = re.compile('"([^"]*)"')


def jakbyco(linie):
    for l in linie:
        if len(l) == 0:
            raise PustaLinia
    k = ""
    for l in linie:
        if l.startswith('"'):
            if k == "msgid":
                msgid += quot.search(l)
            elif k == "msgid_plural":
                msgid_plural += quot.search(l)
            elif k == "msgstr":
                msgstr += quot.search(l)

        elif l.startswith("msgid "):
            msgid = quot.search(l)
            k = "msgid"
        elif l.startswith("msgid_plural "):
            msgid_plural = quot.search(l)
            k = "msgid_plural"
        elif l.startswith("msgstr "):
            msgstr = quot.search(l)
            k = "msgstr"
#        elif l.startswith(msgstr[


class PustaLinia(Exception):
    pass


class baza(Object):

    def __init__(opened):
        self.wpisy = []


class wpis(Object):

    def __init__(listoflines):
        self.listoflines = listoflines
        for l in linie:
            if len(l) == 0:
                raise PustaLinia


class metadane(wpis):
    pass
